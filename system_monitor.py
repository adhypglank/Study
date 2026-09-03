#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
system_monitor.py - System Performance Monitoring
Real-time monitoring dengan alerts dan optimization
Copyright © 2026 Adi Putra (Adhyp Glank)
"""

import os
import sys
import psutil
import threading
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque
from dataclasses import dataclass, asdict
from enum import Enum
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert level enumeration"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"


@dataclass
class PerformanceMetric:
    """Performance metric data class"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_free_gb: float
    gpu_percent: float = 0.0
    gpu_memory_mb: float = 0.0
    network_io_bytes_sent: float = 0.0
    network_io_bytes_recv: float = 0.0
    process_count: int = 0
    thread_count: int = 0
    swap_percent: float = 0.0


@dataclass
class SystemAlert:
    """System alert data class"""
    timestamp: str
    level: AlertLevel
    component: str
    message: str
    value: float = 0.0
    threshold: float = 0.0


class SystemMonitor:
    """Advanced system performance monitoring"""
    
    def __init__(self, history_size: int = 1000, alert_callback=None):
        """
        Initialize System Monitor
        
        Args:
            history_size: Maximum number of metrics to keep
            alert_callback: Callback function untuk alerts
        """
        self.history: deque = deque(maxlen=history_size)
        self.alerts: deque = deque(maxlen=100)
        self.alert_callback = alert_callback
        self.monitoring_active = False
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'gpu_percent': 85.0,
            'swap_percent': 50.0
        }
        self.baseline: Optional[PerformanceMetric] = None
        self.peak_usage: Dict[str, float] = {
            'cpu': 0.0,
            'memory': 0.0,
            'disk': 0.0
        }
        self.low_usage: Dict[str, float] = {
            'cpu': 100.0,
            'memory': 100.0,
            'disk': 100.0
        }
        self.network_start: Optional[Tuple[float, float]] = None
        
    def start_monitoring(self, interval: float = 1.0) -> None:
        """
        Start background monitoring
        
        Args:
            interval: Monitoring interval in seconds
        """
        self.monitoring_active = True
        monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        monitor_thread.start()
        logger.info("🟢 System monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring"""
        self.monitoring_active = False
        logger.info("🔴 System monitoring stopped")
    
    def _monitoring_loop(self, interval: float) -> None:
        """Internal monitoring loop"""
        while self.monitoring_active:
            try:
                metric = self._collect_metrics()
                self.history.append(metric)
                self._check_thresholds(metric)
                time.sleep(interval)
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self) -> PerformanceMetric:
        """Collect system performance metrics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()
            
            # Disk
            disk_usage = psutil.disk_usage('/')
            
            # Network
            if self.network_start is None:
                net_io = psutil.net_io_counters()
                self.network_start = (net_io.bytes_sent, net_io.bytes_recv)
            
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent - (self.network_start[0] or 0)
            bytes_recv = net_io.bytes_recv - (self.network_start[1] or 0)
            
            # Process and thread count
            process_count = len(psutil.pids())
            thread_count = threading.active_count()
            
            # GPU metrics (simplified - would need gpu-specific library in production)
            gpu_percent = 0.0
            gpu_memory_mb = 0.0
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_percent = gpus[0].load * 100
                    gpu_memory_mb = gpus[0].memoryUsed
            except:
                pass
            
            metric = PerformanceMetric(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=virtual_mem.percent,
                memory_mb=virtual_mem.used / (1024 * 1024),
                memory_available_mb=virtual_mem.available / (1024 * 1024),
                disk_percent=disk_usage.percent,
                disk_free_gb=disk_usage.free / (1024**3),
                gpu_percent=gpu_percent,
                gpu_memory_mb=gpu_memory_mb,
                network_io_bytes_sent=bytes_sent,
                network_io_bytes_recv=bytes_recv,
                process_count=process_count,
                thread_count=thread_count,
                swap_percent=swap_mem.percent
            )
            
            # Update peak and low usage
            self._update_peak_low(metric)
            
            return metric
            
        except Exception as e:
            logger.error(f"❌ Failed to collect metrics: {e}")
            return PerformanceMetric(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_mb=0.0,
                memory_available_mb=0.0,
                disk_percent=0.0,
                disk_free_gb=0.0
            )
    
    def _update_peak_low(self, metric: PerformanceMetric) -> None:
        """Update peak and low usage statistics"""
        self.peak_usage['cpu'] = max(self.peak_usage['cpu'], metric.cpu_percent)
        self.peak_usage['memory'] = max(self.peak_usage['memory'], metric.memory_percent)
        self.peak_usage['disk'] = max(self.peak_usage['disk'], metric.disk_percent)
        
        self.low_usage['cpu'] = min(self.low_usage['cpu'], metric.cpu_percent)
        self.low_usage['memory'] = min(self.low_usage['memory'], metric.memory_percent)
        self.low_usage['disk'] = min(self.low_usage['disk'], metric.disk_percent)
    
    def _check_thresholds(self, metric: PerformanceMetric) -> None:
        """Check metrics against thresholds and generate alerts"""
        checks = [
            ('CPU', metric.cpu_percent, 'cpu_percent'),
            ('Memory', metric.memory_percent, 'memory_percent'),
            ('Disk', metric.disk_percent, 'disk_percent'),
            ('Swap', metric.swap_percent, 'swap_percent'),
            ('GPU', metric.gpu_percent, 'gpu_percent'),
        ]
        
        for component, value, threshold_key in checks:
            threshold = self.thresholds.get(threshold_key, 100.0)
            
            if value >= threshold:
                level = AlertLevel.CRITICAL if value >= threshold * 1.1 else AlertLevel.WARNING
                alert = SystemAlert(
                    timestamp=datetime.now().isoformat(),
                    level=level,
                    component=component,
                    message=f"{component} usage at {value:.1f}% (threshold: {threshold:.1f}%)",
                    value=value,
                    threshold=threshold
                )
                self.alerts.append(alert)
                
                if self.alert_callback:
                    self.alert_callback(alert)
                
                logger.warning(f"⚠️  {alert.message}")
    
    def get_current_metrics(self) -> Optional[PerformanceMetric]:
        """Get current performance metrics"""
        if self.history:
            return self.history[-1]
        return self._collect_metrics()
    
    def get_average_metrics(self, minutes: int = 5) -> Optional[PerformanceMetric]:
        """Get average metrics over time period"""
        if not self.history:
            return None
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.history
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        if not recent_metrics:
            return None
        
        avg_metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            cpu_percent=sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            memory_percent=sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            memory_mb=sum(m.memory_mb for m in recent_metrics) / len(recent_metrics),
            memory_available_mb=sum(m.memory_available_mb for m in recent_metrics) / len(recent_metrics),
            disk_percent=sum(m.disk_percent for m in recent_metrics) / len(recent_metrics),
            disk_free_gb=sum(m.disk_free_gb for m in recent_metrics) / len(recent_metrics),
            gpu_percent=sum(m.gpu_percent for m in recent_metrics) / len(recent_metrics),
            gpu_memory_mb=sum(m.gpu_memory_mb for m in recent_metrics) / len(recent_metrics),
            network_io_bytes_sent=sum(m.network_io_bytes_sent for m in recent_metrics) / len(recent_metrics),
            network_io_bytes_recv=sum(m.network_io_bytes_recv for m in recent_metrics) / len(recent_metrics),
            process_count=int(sum(m.process_count for m in recent_metrics) / len(recent_metrics)),
            thread_count=int(sum(m.thread_count for m in recent_metrics) / len(recent_metrics)),
            swap_percent=sum(m.swap_percent for m in recent_metrics) / len(recent_metrics)
        )
        
        return avg_metric
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent system alerts"""
        alerts = list(self.alerts)[-limit:]
        return [asdict(alert) for alert in alerts]
    
    def get_system_health(self) -> Dict:
        """Get overall system health status"""
        current = self.get_current_metrics()
        
        if not current:
            return {"status": "UNKNOWN"}
        
        # Determine health status
        critical_count = sum(1 for check in [
            current.cpu_percent > self.thresholds['cpu_percent'] * 1.1,
            current.memory_percent > self.thresholds['memory_percent'] * 1.1,
            current.disk_percent > self.thresholds['disk_percent'] * 1.1
        ] if check)
        
        warning_count = sum(1 for check in [
            current.cpu_percent > self.thresholds['cpu_percent'],
            current.memory_percent > self.thresholds['memory_percent'],
            current.disk_percent > self.thresholds['disk_percent']
        ] if check)
        
        if critical_count > 0:
            status = "CRITICAL"
        elif warning_count > 0:
            status = "WARNING"
        else:
            status = "HEALTHY"
        
        return {
            "status": status,
            "timestamp": current.timestamp,
            "cpu_percent": current.cpu_percent,
            "memory_percent": current.memory_percent,
            "disk_percent": current.disk_percent,
            "memory_mb": current.memory_mb,
            "memory_available_mb": current.memory_available_mb,
            "disk_free_gb": current.disk_free_gb,
            "critical_alerts": critical_count,
            "warning_alerts": warning_count,
            "process_count": current.process_count,
            "thread_count": current.thread_count
        }
    
    def get_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        current = self.get_current_metrics()
        avg_5min = self.get_average_metrics(minutes=5)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "monitoring_duration": len(self.history),
            "current_metrics": asdict(current) if current else {},
            "average_5min": asdict(avg_5min) if avg_5min else {},
            "peak_usage": self.peak_usage,
            "low_usage": self.low_usage,
            "recent_alerts": self.get_recent_alerts(limit=10),
            "health_status": self.get_system_health()
        }
        
        return report
    
    def set_threshold(self, component: str, threshold: float) -> bool:
        """Set alert threshold untuk component"""
        threshold_key = f"{component.lower()}_percent"
        if threshold_key in self.thresholds:
            self.thresholds[threshold_key] = threshold
            logger.info(f"✅ Threshold set: {component}={threshold}%")
            return True
        return False
    
    def export_metrics(self, filepath: str = "metrics_export.json") -> bool:
        """Export semua collected metrics ke file"""
        try:
            metrics_list = [asdict(m) for m in self.history]
            with open(filepath, 'w') as f:
                json.dump(metrics_list, f, indent=2)
            logger.info(f"✅ Exported {len(metrics_list)} metrics to {filepath}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to export metrics: {e}")
            return False


def alert_handler(alert: SystemAlert):
    """Default alert handler"""
    if alert.level == AlertLevel.CRITICAL:
        logger.critical(f"🔴 CRITICAL: {alert.component} - {alert.message}")
    elif alert.level == AlertLevel.WARNING:
        logger.warning(f"🟡 WARNING: {alert.component} - {alert.message}")


# Global monitor instance
_monitor_instance: Optional[SystemMonitor] = None


def get_monitor() -> SystemMonitor:
    """Get global system monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SystemMonitor(alert_callback=alert_handler)
    return _monitor_instance


if __name__ == "__main__":
    print("\n" + "="*70)
    print("📊 SYSTEM MONITOR - REAL-TIME PERFORMANCE TRACKING")
    print("="*70 + "\n")
    
    monitor = get_monitor()
    monitor.start_monitoring(interval=2.0)
    
    print("Monitoring system performance for 30 seconds...")
    print("(Press Ctrl+C to stop)\n")
    
    try:
        for i in range(15):
            health = monitor.get_system_health()
            print(f"[{i+1}] Status: {health['status']:10} | "
                  f"CPU: {health['cpu_percent']:5.1f}% | "
                  f"Memory: {health['memory_percent']:5.1f}% | "
                  f"Disk: {health['disk_percent']:5.1f}%")
            time.sleep(2)
        
        print("\n" + "="*70)
        print("📊 PERFORMANCE REPORT")
        print("="*70 + "\n")
        
        report = monitor.get_performance_report()
        print(f"Monitoring Duration: {report['monitoring_duration']} samples")
        print(f"Peak CPU Usage: {report['peak_usage']['cpu']:.1f}%")
        print(f"Peak Memory Usage: {report['peak_usage']['memory']:.1f}%")
        print(f"Peak Disk Usage: {report['peak_usage']['disk']:.1f}%")
        print(f"\nHealth Status: {report['health_status']['status']}")
        print(f"Recent Alerts: {len(report['recent_alerts'])}")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")
    finally:
        monitor.stop_monitoring()
        print("✅ System monitor ready for integration")
        print("="*70 + "\n")
