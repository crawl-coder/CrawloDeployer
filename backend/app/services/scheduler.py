# /backend/app/services/scheduler.py

import threading
import logging
from datetime import datetime
from typing import Optional, List

import redis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.db.session import engine  # 使用 engine，非 SessionLocal
from app.tasks.crawler_tasks import run_generic_script  # ✅ 通用任务
from app.models.task import Task, TaskDistributionMode
from app.models.node import NodeStatus

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler: Optional[BackgroundScheduler] = None
        self.redis_client: Optional[redis.Redis] = None
        self.listener_thread: Optional[threading.Thread] = None

    def _get_db(self) -> Session:
        """获取线程本地 Session"""
        return Session(bind=engine)

    def _schedule_job(self, task_id: int):
        """
        包装函数：根据任务 ID 从数据库获取任务信息并提交到 Celery
        """
        db = self._get_db()
        try:
            db_task = crud.task.get(db, id=task_id)
            if not db_task or not db_task.is_enabled:
                logger.warning(f"Task {task_id} not found or disabled, skipping.")
                return

            project_name = db_task.project.name
            entrypoint = db_task.entrypoint or "run.py"  # ✅ 支持 entrypoint
            args = db_task.args or {}
            env = {"RUN_MODE": "scheduled"}

            # 根据任务分发模式确定目标节点
            target_nodes = self._get_target_nodes(db, db_task)
            
            if not target_nodes:
                logger.warning(f"No target nodes available for task {task_id}, skipping.")
                return

            # 如果有多个目标节点，可以分发到多个节点并行执行
            # 这里简化处理，只分发到第一个可用节点
            # 在实际实现中，可以根据需求进行更复杂的分发策略
            for node in target_nodes:
                # 提交通用任务
                run_generic_script.delay(
                    original_task_id=db_task.id,
                    project_name=project_name,
                    entrypoint=entrypoint,
                    args=args,
                    env=env
                )
                logger.info(f"Scheduled task {task_id} via Celery to node {node.hostname}")
                break  # 只分发到一个节点，如果需要分发到多个节点，可以移除这个break
        except Exception as e:
            logger.error(f"Error in _schedule_job for task {task_id}: {e}")
        finally:
            db.close()

    def _get_target_nodes(self, db: Session, task: Task) -> List:
        """
        根据任务的分发模式获取目标节点列表
        """
        if task.distribution_mode == TaskDistributionMode.ANY:
            # 任意节点模式，返回所有在线节点
            stmt = crud.node.select().where(crud.node.model.status == NodeStatus.ONLINE)
            result = db.execute(stmt)
            return list(result.scalars().all())
        elif task.distribution_mode == TaskDistributionMode.SPECIFIC:
            # 指定单个节点模式
            if task.target_node_id:
                node = crud.node.get(db, id=task.target_node_id)
                if node and node.status == NodeStatus.ONLINE:
                    return [node]
            return []
        elif task.distribution_mode == TaskDistributionMode.MULTIPLE:
            # 指定多个节点模式
            if task.target_node_ids:
                nodes = []
                for node_id in task.target_node_ids:
                    node = crud.node.get(db, id=node_id)
                    if node and node.status == NodeStatus.ONLINE:
                        nodes.append(node)
                return nodes
            return []
        elif task.distribution_mode == TaskDistributionMode.TAG_BASED:
            # 基于标签分发模式
            if task.target_node_tags:
                # 这里简化处理，实际实现中可以根据标签进行更复杂的匹配
                stmt = crud.node.select().where(
                    crud.node.model.status == NodeStatus.ONLINE,
                    crud.node.model.tags.contains(task.target_node_tags)
                )
                result = db.execute(stmt)
                return list(result.scalars().all())
            return []
        else:
            # 默认返回所有在线节点
            stmt = crud.node.select().where(crud.node.model.status == NodeStatus.ONLINE)
            result = db.execute(stmt)
            return list(result.scalars().all())

    def add_task(self, db_task: Task):
        """将数据库任务添加到调度器"""
        if not db_task.is_enabled or not db_task.cron_expression:
            return

        try:
            # 解析 cron 表达式
            cron_fields = self._parse_cron(db_task.cron_expression)
            self.scheduler.add_job(
                self._schedule_job,
                "cron",
                id=str(db_task.id),
                name=db_task.name,
                args=[db_task.id],
                **cron_fields
            )
            logger.info(f"Task '{db_task.name}' (ID: {db_task.id}) added to scheduler.")
        except Exception as e:
            logger.error(f"Error adding task {db_task.id} to scheduler: {e}")

    def remove_task(self, task_id: int):
        """从调度器移除任务"""
        try:
            self.scheduler.remove_job(str(task_id))
            logger.info(f"Task ID: {task_id} removed from scheduler.")
        except JobLookupError:
            logger.debug(f"Task ID: {task_id} not found in scheduler.")

    def has_task(self, task_id: int) -> bool:
        """检查任务是否已在调度器中"""
        return self.scheduler.get_job(str(task_id)) is not None

    def _parse_cron(self, cron_expr: str) -> dict:
        """解析 cron 表达式为 apscheduler 参数"""
        parts = cron_expr.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expr}")
        return {
            "minute": parts[0],
            "hour": parts[1],
            "day": parts[2],
            "month": parts[3],
            "day_of_week": parts[4]
        }

    def sync_jobs_from_db(self):
        """从数据库同步所有启用的定时任务"""
        logger.info("🔄 Syncing jobs from DB to scheduler...")
        with self._get_db() as db:
            enabled_tasks = crud.task.get_enabled_tasks(db)
            current_job_ids = {job.id for job in self.scheduler.get_jobs()}

            # 移除数据库中已删除的任务
            for job_id in current_job_ids:
                if not any(str(t.id) == job_id for t in enabled_tasks):
                    self.remove_task(int(job_id))

            # 添加新任务
            for task in enabled_tasks:
                if str(task.id) not in current_job_ids:
                    self.add_task(task)

    def _check_node_heartbeats(self):
        """定期检查节点心跳"""
        logger.debug("🔍 Checking node heartbeats...")
        try:
            with self._get_db() as db:
                all_nodes = crud.node.get_multi(db)
                updated = False
                for node in all_nodes:
                    heartbeat_key = f"nodes:heartbeat:{node.hostname}"
                    try:
                        if self.redis_client.exists(heartbeat_key):
                            if node.status != NodeStatus.ONLINE:
                                crud.node.heartbeat(db, hostname=node.hostname)
                                logger.info(f"Node {node.hostname} is ONLINE")
                        else:
                            if node.status != NodeStatus.OFFLINE:
                                crud.node.mark_offline(db, hostname=node.hostname)
                                logger.info(f"Node {node.hostname} marked OFFLINE")
                                updated = True
                    except Exception as e:
                        logger.warning(f"Failed to check heartbeat for {node.hostname}: {e}")
                if updated:
                    db.commit()
        except Exception as e:
            logger.error(f"Error in _check_node_heartbeats: {e}")

    def _listen_for_node_registrations(self):
        """监听 Redis 发布/订阅，实时注册节点"""
        try:
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe("nodes:register")
            logger.info("👂 Listening for new node registrations...")
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        hostname = message['data']
                        logger.info(f"Registering new node: {hostname}")
                        with self._get_db() as db:
                            crud.node.register_or_update(db, hostname=hostname)
                    except Exception as e:
                        logger.error(f"Failed to register node: {e}")
        except Exception as e:
            logger.critical(f"Node registration listener crashed: {e}")

    def start(self):
        """启动调度器"""
        if self.scheduler and self.scheduler.running:
            logger.warning("Scheduler is already running.")
            return

        # 初始化 Redis
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis_client.ping()
        except Exception as e:
            logger.critical(f"Failed to connect to Redis: {e}")
            raise

        # 初始化调度器
        self.scheduler = BackgroundScheduler(
            timezone=settings.TIMEZONE or "Asia/Shanghai"
        )

        # 同步任务
        self.sync_jobs_from_db()

        # 添加节点心跳检查
        self.scheduler.add_job(
            self._check_node_heartbeats,
            "interval",
            seconds=settings.NODE_HEARTBEAT_CHECK_INTERVAL or 30,
            id="node_heartbeat_check",
            name="Node Heartbeat Monitor"
        )

        # 启动注册监听线程
        self.listener_thread = threading.Thread(
            target=self._listen_for_node_registrations,
            daemon=True
        )
        self.listener_thread.start()

        self.scheduler.start()
        logger.info("✅ Scheduler and Node Monitor started.")

    def shutdown(self):
        """安全关闭"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("🛑 Scheduler shut down.")
        # Redis 和线程会随进程退出自动清理

    def is_running(self) -> bool:
        """检查调度器是否运行"""
        return self.scheduler is not None and self.scheduler.running

    def get_job_count(self) -> int:
        """获取当前调度器中的任务数量"""
        if self.scheduler:
            return len(self.scheduler.get_jobs())
        return 0


# 创建全局实例
scheduler_service = SchedulerService()