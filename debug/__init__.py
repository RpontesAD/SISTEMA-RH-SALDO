"""
Módulo de Debug - Sistema completo de debug e monitoramento
"""

from .debug_system import (
    logger, 
    DebugManager, 
    DatabaseDebugger, 
    AuthDebugger, 
    BusinessLogicDebugger,
    debug_decorator,
    debug_streamlit_component,
    debug_session_state
)

from .debug_panel import (
    show_debug_panel,
    add_debug_to_page,
    show_debug_metrics
)

from .debug_config import (
    DEBUG_SETTINGS,
    get_debug_setting,
    is_debug_enabled,
    set_debug_setting
)

__all__ = [
    'logger',
    'DebugManager',
    'DatabaseDebugger', 
    'AuthDebugger',
    'BusinessLogicDebugger',
    'debug_decorator',
    'debug_streamlit_component',
    'debug_session_state',
    'show_debug_panel',
    'add_debug_to_page',
    'show_debug_metrics',
    'DEBUG_SETTINGS',
    'get_debug_setting',
    'is_debug_enabled',
    'set_debug_setting'
]