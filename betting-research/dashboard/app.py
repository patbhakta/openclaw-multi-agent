"""
Super Bowl Paper Trading Dashboard

Simple Streamlit dashboard for monitoring Super Bowl paper trading.
Based on openalgo Dashboard API integration pattern.

Pages:
1. Portfolio Overview (Home) - P&L, win rate, trades count, status metrics
2. Paper Trades - Table of recent paper trades with filters
3. Signals - List of active betting signals with filters
4. Bot Controls - Start/Stop bot, API Analyzer Mode toggle, system logs
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db import DatabaseManager
from src.security.audit_logger import AuditLogger


class DashboardApp:
    """Main dashboard application"""

    def __init__(self):
        """Initialize dashboard"""
        st.set_page_config(
            page_title="🏈 Super Bowl Paper Trading",
            page_icon="🏈",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Initialize database connection
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'betting_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }

        self.db_manager = None
        self.audit_logger = None

    def connect_to_db(self) -> bool:
        """Connect to database"""
        try:
            self.db_manager = DatabaseManager(self.db_config)
            self.audit_logger = AuditLogger(self.db_manager.engine)
            return True
        except Exception as e:
            st.error(f"❌ Failed to connect to database: {str(e)}")
            return False

    def get_portfolio_stats(self) -> Dict:
        """Get portfolio statistics"""
        try:
            if not self.db_manager:
                return {
                    'paper_pnl': 0.0,
                    'win_rate': 0.0,
                    'total_trades': 0,
                    'analyzer_mode': False,
                    'bot_status': 'IDLE',
                    'api_keys_loaded': 0,
                    'dashboard_api_connected': False
                }

            with self.db_manager.get_session() as session:
                from src.models.paper_trade import PaperTrade

                # Get executed trades
                executed_trades = session.query(PaperTrade).filter(
                    PaperTrade.status == 'EXECUTED'
                ).all()

                # Calculate P&L
                paper_pnl = sum(
                    float(trade.pnl) if trade.pnl else 0.0
                    for trade in executed_trades
                )

                # Calculate win rate
                winning_trades = [
                    trade for trade in executed_trades
                    if trade.pnl and float(trade.pnl) > 0
                ]
                win_rate = (
                    len(winning_trades) / len(executed_trades) * 100
                    if executed_trades else 0.0
                )

                # Get total trades count
                total_trades = len(executed_trades)

                # Check analyzer mode status (from audit log or config)
                analyzer_mode = self._check_analyzer_mode(session)

                # Check bot status (from audit log or config)
                bot_status = self._check_bot_status(session)

                # Count API keys (from database)
                from src.models.api_key import APIKey
                api_keys_count = session.query(APIKey).filter(
                    APIKey.expires_at > datetime.now()
                ).count()

                # Dashboard API connection status
                dashboard_connected = self._check_dashboard_connection()

                return {
                    'paper_pnl': paper_pnl,
                    'win_rate': round(win_rate, 1),
                    'total_trades': total_trades,
                    'analyzer_mode': analyzer_mode,
                    'bot_status': bot_status,
                    'api_keys_loaded': api_keys_count,
                    'dashboard_api_connected': dashboard_connected
                }

        except Exception as e:
            st.error(f"❌ Failed to get portfolio stats: {str(e)}")
            return {
                'paper_pnl': 0.0,
                'win_rate': 0.0,
                'total_trades': 0,
                'analyzer_mode': False,
                'bot_status': 'IDLE',
                'api_keys_loaded': 0,
                'dashboard_api_connected': False
            }

    def _check_analyzer_mode(self, session) -> bool:
        """Check API Analyzer Mode status"""
        try:
            from src.models.security_event import SecurityEvent
            recent_event = session.query(SecurityEvent).filter(
                SecurityEvent.event_type == 'analyzer_mode_change'
            ).order_by(SecurityEvent.created_at.desc()).first()

            if recent_event:
                # Check if enabled in details
                return 'ENABLED' in recent_event.details.upper()

            return False
        except Exception:
            return False

    def _check_bot_status(self, session) -> str:
        """Check bot status"""
        try:
            from src.models.security_event import SecurityEvent
            recent_event = session.query(SecurityEvent).filter(
                SecurityEvent.event_type == 'bot_status_change'
            ).order_by(SecurityEvent.created_at.desc()).first()

            if recent_event:
                return recent_event.details.get('status', 'IDLE') if isinstance(recent_event.details, dict) else 'IDLE'

            return 'IDLE'
        except Exception:
            return 'IDLE'

    def _check_dashboard_connection(self) -> bool:
        """Check Dashboard API connection"""
        try:
            # This would check actual Dashboard API connectivity
            # For now, simulate based on environment
            return os.getenv('DASHBOARD_API_URL') is not None
        except Exception:
            return False

    def get_paper_trades(self, status_filter: Optional[str] = None) -> List[Dict]:
        """Get paper trades with optional status filter"""
        try:
            if not self.db_manager:
                return []

            with self.db_manager.get_session() as session:
                from src.models.paper_trade import PaperTrade

                query = session.query(PaperTrade)

                if status_filter and status_filter != 'ALL':
                    query = query.filter(PaperTrade.status == status_filter)

                trades = query.order_by(PaperTrade.created_at.desc()).limit(50).all()

                return [
                    {
                        'trade_id': trade.trade_id,
                        'prop_id': trade.prop_id,
                        'action': trade.action,
                        'amount': float(trade.amount) if trade.amount else 0.0,
                        'status': trade.status,
                        'pnl': float(trade.pnl) if trade.pnl else 0.0,
                        'created_at': trade.created_at.isoformat() if trade.created_at else ''
                    }
                    for trade in trades
                ]

        except Exception as e:
            st.error(f"❌ Failed to get paper trades: {str(e)}")
            return []

    def get_signals(self, action_filter: Optional[str] = None) -> List[Dict]:
        """Get betting signals with optional action filter"""
        try:
            if not self.db_manager:
                return []

            with self.db_manager.get_session() as session:
                from src.models.paper_trade import PaperTrade

                # For now, use paper trades as signals (would have separate signals table in production)
                query = session.query(PaperTrade).filter(
                    PaperTrade.status.in_(['PENDING', 'EXECUTED'])
                )

                if action_filter and action_filter != 'ALL':
                    query = query.filter(PaperTrade.action == action_filter)

                trades = query.order_by(PaperTrade.created_at.desc()).limit(20).all()

                return [
                    {
                        'prop_id': trade.prop_id,
                        'market_type': getattr(trade, 'market_type', 'nfl_superbowl'),
                        'action': trade.action,
                        'confidence': getattr(trade, 'confidence', 'MEDIUM'),
                        'edge': getattr(trade, 'edge', 0.0),
                        'market_price': float(trade.amount) if trade.amount else 0.0,
                        'suggested_price': float(trade.amount) * 1.05 if trade.amount else 0.0,
                        'reasoning': getattr(trade, 'reasoning', 'Generated by prediction engine'),
                        'timestamp': trade.created_at.isoformat() if trade.created_at else ''
                    }
                    for trade in trades
                ]

        except Exception as e:
            st.error(f"❌ Failed to get signals: {str(e)}")
            return []

    def get_system_logs(self) -> List[Dict]:
        """Get recent system logs"""
        try:
            if not self.db_manager:
                return []

            with self.db_manager.get_session() as session:
                from src.models.security_event import SecurityEvent

                logs = session.query(SecurityEvent).order_by(
                    SecurityEvent.created_at.desc()
                ).limit(50).all()

                return [
                    {
                        'timestamp': log.created_at.isoformat() if log.created_at else '',
                        'severity': log.severity,
                        'event_type': log.event_type,
                        'details': str(log.details) if log.details else '',
                        'user_id': log.user_id if log.user_id else 'SYSTEM'
                    }
                    for log in logs
                ]

        except Exception as e:
            st.error(f"❌ Failed to get system logs: {str(e)}")
            return []

    def run_portfolio_overview(self):
        """Portfolio Overview page"""
        st.header("📊 Portfolio Overview")

        # Get portfolio stats
        stats = self.get_portfolio_stats()

        # Metrics row
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Paper P&L",
                f"${stats['paper_pnl']:+.2f}",
                delta_color="normal" if stats['paper_pnl'] >= 0 else "inverse"
            )

        with col2:
            st.metric(
                "Win Rate",
                f"{stats['win_rate']:.1f}%",
                delta=f"{stats['win_rate'] - 50:+.1f}%" if stats['win_rate'] > 0 else None
            )

        with col3:
            st.metric(
                "Total Trades",
                stats['total_trades']
            )

        st.markdown("---")

        # Status metrics
        col4, col5, col6, col7 = st.columns(4)

        with col4:
            st.metric(
                "Analyzer Mode",
                "ENABLED" if stats['analyzer_mode'] else "DISABLED",
                delta="🔒" if stats['analyzer_mode'] else None
            )

        with col5:
            st.metric(
                "Dashboard API",
                "CONNECTED" if stats['dashboard_api_connected'] else "DISCONNECTED",
                delta="✅" if stats['dashboard_api_connected'] else "❌"
            )

        with col6:
            st.metric(
                "Bot Status",
                stats['bot_status'],
                delta="🟢" if stats['bot_status'] == 'ACTIVE' else "🔴"
            )

        with col7:
            st.metric(
                "API Keys",
                stats['api_keys_loaded'],
                delta=f"{stats['api_keys_loaded']} keys loaded"
            )

        st.markdown("---")

        # Additional info
        st.subheader("System Information")

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.info(f"""
            **Super Bowl Information:**
            - **Date:** February 9, 2026
            - **Status:** Paper trading mode only
            - **Risk:** No real money involved
            """)

        with info_col2:
            st.info(f"""
            **Dashboard Settings:**
            - **Auto-refresh:** Every 30 seconds
            - **Timezone:** UTC
            - **Paper Trading:** API Analyzer Mode
            """)

    def run_paper_trades(self):
        """Paper Trades page"""
        st.header("📋 Paper Trades")

        # Status filter
        status_filter = st.selectbox(
            "Filter by Status",
            ["ALL", "PENDING", "EXECUTED", "FAILED"],
            key="paper_trades_filter"
        )

        # Get trades
        trades = self.get_paper_trades(status_filter=status_filter)

        # Display table
        if trades:
            df = pd.DataFrame(trades)

            # Format columns
            df['amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
            df['pnl'] = df['pnl'].apply(lambda x: f"${x:+.2f}")
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

            # Reorder columns
            df = df[['trade_id', 'prop_id', 'action', 'amount', 'status', 'pnl', 'created_at']]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No paper trades found.")

        # Statistics
        if trades:
            st.markdown("---")
            st.subheader("Trade Statistics")

            df = pd.DataFrame(trades)

            stat_col1, stat_col2, stat_col3 = st.columns(3)

            with stat_col1:
                total_trades = len(trades)
                st.metric("Total Trades", total_trades)

            with stat_col2:
                pending_trades = len([t for t in trades if t['status'] == 'PENDING'])
                st.metric("Pending Trades", pending_trades)

            with stat_col3:
                executed_trades = len([t for t in trades if t['status'] == 'EXECUTED'])
                st.metric("Executed Trades", executed_trades)

    def run_signals(self):
        """Signals page"""
        st.header("📡 Betting Signals")

        # Action filter
        action_filter = st.selectbox(
            "Filter by Action",
            ["ALL", "BET", "PASS"],
            key="signals_filter"
        )

        # Get signals
        signals = self.get_signals(action_filter=action_filter)

        # Display table
        if signals:
            df = pd.DataFrame(signals)

            # Format columns
            df['edge'] = df['edge'].apply(lambda x: f"{x:.1%}")
            df['market_price'] = df['market_price'].apply(lambda x: f"${x:.2f}")
            df['suggested_price'] = df['suggested_price'].apply(lambda x: f"${x:.2f}")
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

            # Reorder columns
            df = df[['prop_id', 'market_type', 'action', 'confidence', 'edge', 'market_price', 'suggested_price', 'reasoning', 'timestamp']]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No active betting signals found.")

        # Statistics
        if signals:
            st.markdown("---")
            st.subheader("Signal Statistics")

            df = pd.DataFrame(signals)

            stat_col1, stat_col2, stat_col3 = st.columns(3)

            with stat_col1:
                bet_signals = len([s for s in signals if s['action'] == 'BET'])
                st.metric("BET Signals", bet_signals)

            with stat_col2:
                pass_signals = len([s for s in signals if s['action'] == 'PASS'])
                st.metric("PASS Signals", pass_signals)

            with stat_col3:
                high_confidence = len([s for s in signals if s['confidence'] == 'HIGH'])
                st.metric("High Confidence", high_confidence)

    def run_bot_controls(self):
        """Bot Controls page"""
        st.header("🤖 Bot Controls")

        # Get current status
        stats = self.get_portfolio_stats()

        # Bot status display
        status_col1, status_col2 = st.columns(2)

        with status_col1:
            st.info(f"""
            **Current Bot Status:** {stats['bot_status']}

            **Analyzer Mode:** {'ENABLED' if stats['analyzer_mode'] else 'DISABLED'}

            **API Keys Loaded:** {stats['api_keys_loaded']}
            """)

        with status_col2:
            st.info(f"""
            **Dashboard API:** {'CONNECTED' if stats['dashboard_api_connected'] else 'DISCONNECTED'}

            **Database:** {'CONNECTED' if self.db_manager else 'DISCONNECTED'}

            **Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            """)

        st.markdown("---")

        # Control buttons
        st.subheader("Bot Controls")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🟢 Start Bot", key="start_bot", use_container_width=True):
                self._start_bot()
                st.success("✅ Bot started!")
                st.rerun()

        with col2:
            if st.button("🔴 Stop Bot", key="stop_bot", use_container_width=True):
                self._stop_bot()
                st.success("✅ Bot stopped!")
                st.rerun()

        with col3:
            if st.button("🔄 Toggle Analyzer Mode", key="toggle_analyzer", use_container_width=True):
                self._toggle_analyzer_mode()
                st.success("✅ Analyzer Mode toggled!")
                st.rerun()

        st.markdown("---")

        # System logs
        st.subheader("System Logs")

        logs = self.get_system_logs()

        if logs:
            df = pd.DataFrame(logs)

            # Format columns
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No system logs found.")

    def _start_bot(self):
        """Start bot"""
        try:
            if self.audit_logger:
                self.audit_logger.log_security_event(
                    severity='INFO',
                    event_type='bot_status_change',
                    user_id=0,  # System
                    details={'status': 'ACTIVE'}
                )
        except Exception as e:
            st.error(f"❌ Failed to start bot: {str(e)}")

    def _stop_bot(self):
        """Stop bot"""
        try:
            if self.audit_logger:
                self.audit_logger.log_security_event(
                    severity='INFO',
                    event_type='bot_status_change',
                    user_id=0,  # System
                    details={'status': 'IDLE'}
                )
        except Exception as e:
            st.error(f"❌ Failed to stop bot: {str(e)}")

    def _toggle_analyzer_mode(self):
        """Toggle API Analyzer Mode"""
        try:
            if self.audit_logger:
                # Get current status
                stats = self.get_portfolio_stats()
                new_status = 'ENABLED' if not stats['analyzer_mode'] else 'DISABLED'

                self.audit_logger.log_security_event(
                    severity='INFO',
                    event_type='analyzer_mode_change',
                    user_id=0,  # System
                    details={'analyzer_mode': new_status}
                )
        except Exception as e:
            st.error(f"❌ Failed to toggle analyzer mode: {str(e)}")

    def run(self):
        """Run dashboard"""
        # Connect to database
        if not self.connect_to_db():
            st.error("❌ Failed to initialize database connection. Please check your configuration.")
            return

        # Sidebar navigation
        page = st.sidebar.radio(
            "Navigation",
            ["Portfolio Overview", "Paper Trades", "Signals", "Bot Controls"],
            index=0
        )

        # Auto-refresh
        auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=True)
        if auto_refresh:
            st.toast("Dashboard auto-refreshing every 30 seconds", icon="🔄")

        # Render page
        if page == "Portfolio Overview":
            self.run_portfolio_overview()
        elif page == "Paper Trades":
            self.run_paper_trades()
        elif page == "Signals":
            self.run_signals()
        elif page == "Bot Controls":
            self.run_bot_controls()

        # Auto-refresh
        if auto_refresh:
            time.sleep(30)
            st.rerun()


def main():
    """Main entry point"""
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    import time
    main()
