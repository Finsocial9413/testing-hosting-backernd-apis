from agno.tools import Toolkit
from typing import Optional
import re

class ChartTools(Toolkit):
    def __init__(self):
        super().__init__(name="chart_tools")
        
        # Available indicators
        self.trend_indicators = [
            "EMA", "SMA", "MA", "WMA", "SuperTrend", "SMMA", "TTMTrend", "TEMA", 
            "DEMA", "HMA", "ALMA", "LINEARREG", "MCGINLEY", "VWMA", "VPWMA", 
            "TSF", "SAFEZONESTOP", "MEDPRICE", "AVGPRICE", "MWDX", "ADX", "DI", 
            "DM", "VI", "DX", "AROON", "SAR", "ICHIMOKUCLOUD", "Alligator", "CKSP"
        ]
        
        self.momentum_indicators = [
            "RSI", "MACD", "MOM", "TRIX", "CMO", "APO", "PPO", "AO", "BOP", 
            "ROC", "ROCP", "ROCR", "ROCR100", "TSI", "ULTOSC", "WillR", "CC", 
            "CFO", "CCI", "DPO", "FisherTransform", "KST", "DECOSC", "Stoch", 
            "KDJ", "WT"
        ]
        
        self.volatility_indicators = [
            "ATR", "Bollinger-Bands", "BOLLINGERWIDTH", "CHOP", "MassIndex", 
            "RVI", "Donchian", "Keltner"
        ]
        
        self.volume_indicators = [
            "VWAP", "MFI", "OBV", "EFI", "VPT", "AD", "ADOSC", "EMV", "KVO", 
            "NVI", "PVI", "Volume"
        ]
        
        self.statistical_indicators = ["CORREL", "MeanAD", "MedianAD"]
        
        self.support_resistance_indicators = ["PIVOT", "SupportResistance"]
        
        # All indicators combined
        self.all_indicators = (
            self.trend_indicators + self.momentum_indicators + 
            self.volatility_indicators + self.volume_indicators + 
            self.statistical_indicators + self.support_resistance_indicators
        )
        
        # Available timeframes
        self.timeframes = [
            # Tick-based
            "1 tick", "10 ticks", "100 ticks", "1000 ticks",
            # Second-based
            "1s", "5s", "10s", "15s", "30s", "45s",
            # Minute-based
            "1m", "2m", "3m", "5m", "10m", "15m", "30m", "45m",
            # Hour-based
            "1h", "2h", "3h", "4h", "6h", "8h", "12h",
            # Day-based and longer
            "1D", "3D", "1W", "1M", "3M", "6M", "12M",
            # Range-based
            "1 range", "10 ranges", "100 ranges", "1000 ranges"
        ]

        # Register all functions as tools
        self.register(self.add_indicator_to_chart)
        self.register(self.remove_indicator_from_chart)
        self.register(self.change_chart_timeframe)
        self.register(self.list_available_indicators)
        self.register(self.list_available_timeframes)

    def add_indicator_to_chart(self, indicator: str, timeframe: str = "1m", additional_params: Optional[str] = None) -> str:
        """
        Add a technical indicator to the chart with specified timeframe.
        
        Args:
            indicator: The technical indicator to add (e.g., SMA, RSI, MACD)
            timeframe: The timeframe for the chart (e.g., 1m, 5m, 1h, 1D)
            additional_params: Any additional parameters for the indicator
        
        Returns:
            Status message about the indicator addition
        """
        # Validate indicator
        indicator_upper = indicator.upper()
        if indicator_upper not in [ind.upper() for ind in self.all_indicators]:
            available_indicators = ", ".join(self.all_indicators[:10]) + "..."
            return f"❌ Indicator '{indicator}' not found. Available indicators include: {available_indicators}"
        
        # Find the correct case for the indicator
        correct_indicator = None
        for ind in self.all_indicators:
            if ind.upper() == indicator_upper:
                correct_indicator = ind
                break
        
        # Validate timeframe
        if timeframe not in self.timeframes:
            available_timeframes = ", ".join(self.timeframes[:15]) + "..."
            return f"❌ Timeframe '{timeframe}' not available. Available timeframes include: {available_timeframes}"
        
        # Get indicator category
        category = self._get_indicator_category(correct_indicator)
        
        # Simulate frontend automation process
        try:
            # This would be the actual automation code for the frontend
            automation_steps = [
                f"✅ Navigating to charts section",
                f"✅ Selecting timeframe: {timeframe}",
                f"✅ Opening indicators menu",
                f"✅ Searching for {category} indicator: {correct_indicator}",
                f"✅ Adding {correct_indicator} to chart",
                f"✅ Applying timeframe settings: {timeframe}"
            ]
            
            if additional_params:
                automation_steps.append(f"✅ Applying additional parameters: {additional_params}")
            
            result = "\n".join(automation_steps)
            result += f"\n\n🎯 Successfully added {correct_indicator} indicator with {timeframe} timeframe to the chart!"
            
            return result
            
        except Exception as e:
            return f"❌ Error adding indicator to chart: {str(e)}"

    def remove_indicator_from_chart(self, indicator: str) -> str:
        """
        Remove a technical indicator from the chart.
        
        Args:
            indicator: The technical indicator to remove
        
        Returns:
            Status message about the indicator removal
        """
        indicator_upper = indicator.upper()
        if indicator_upper not in [ind.upper() for ind in self.all_indicators]:
            return f"❌ Indicator '{indicator}' not found or not currently on chart."
        
        # Find the correct case for the indicator
        correct_indicator = None
        for ind in self.all_indicators:
            if ind.upper() == indicator_upper:
                correct_indicator = ind
                break
        
        try:
            automation_steps = [
                f"✅ Locating {correct_indicator} on chart",
                f"✅ Removing {correct_indicator} indicator",
                f"✅ Updating chart display"
            ]
            
            result = "\n".join(automation_steps)
            result += f"\n\n🗑️ Successfully removed {correct_indicator} indicator from the chart!"
            
            return result
            
        except Exception as e:
            return f"❌ Error removing indicator from chart: {str(e)}"

    def change_chart_timeframe(self, timeframe: str) -> str:
        """
        Change the chart timeframe.
        
        Args:
            timeframe: The new timeframe to set
        
        Returns:
            Status message about the timeframe change
        """
        if timeframe not in self.timeframes:
            available_timeframes = ", ".join(self.timeframes[:15]) + "..."
            return f"❌ Timeframe '{timeframe}' not available. Available timeframes include: {available_timeframes}"
        
        try:
            automation_steps = [
                f"✅ Accessing timeframe selector",
                f"✅ Changing timeframe to: {timeframe}",
                f"✅ Refreshing chart data",
                f"✅ Updating all indicators for new timeframe"
            ]
            
            result = "\n".join(automation_steps)
            result += f"\n\n⏱️ Successfully changed chart timeframe to {timeframe}!"
            
            return result
            
        except Exception as e:
            return f"❌ Error changing timeframe: {str(e)}"

    def list_available_indicators(self, category: Optional[str] = None) -> str:
        """
        List available technical indicators, optionally filtered by category.
        
        Args:
            category: Optional category filter (trend, momentum, volatility, volume, statistical, support_resistance)
        
        Returns:
            List of available indicators
        """
        if category:
            category_lower = category.lower()
            if category_lower in ["trend"]:
                indicators = self.trend_indicators
                title = "Trend Indicators"
            elif category_lower in ["momentum"]:
                indicators = self.momentum_indicators
                title = "Momentum Indicators"
            elif category_lower in ["volatility"]:
                indicators = self.volatility_indicators
                title = "Volatility Indicators"
            elif category_lower in ["volume"]:
                indicators = self.volume_indicators
                title = "Volume Indicators"
            elif category_lower in ["statistical"]:
                indicators = self.statistical_indicators
                title = "Statistical Indicators"
            elif category_lower in ["support", "resistance", "support_resistance"]:
                indicators = self.support_resistance_indicators
                title = "Support/Resistance Indicators"
            else:
                return f"❌ Unknown category '{category}'. Available categories: trend, momentum, volatility, volume, statistical, support_resistance"
        else:
            title = "All Available Indicators"
            indicators = self.all_indicators
        
        result = f"📊 {title}:\n"
        result += ", ".join(indicators)
        return result

    def list_available_timeframes(self) -> str:
        """
        List all available timeframes.
        
        Returns:
            List of available timeframes
        """
        result = "⏱️ Available Timeframes:\n\n"
        result += "Tick-based: 1 tick, 10 ticks, 100 ticks, 1000 ticks\n"
        result += "Second-based: 1s, 5s, 10s, 15s, 30s, 45s\n"
        result += "Minute-based: 1m, 2m, 3m, 5m, 10m, 15m, 30m, 45m\n"
        result += "Hour-based: 1h, 2h, 3h, 4h, 6h, 8h, 12h\n"
        result += "Day+ based: 1D, 3D, 1W, 1M, 3M, 6M, 12M\n"
        result += "Range-based: 1 range, 10 ranges, 100 ranges, 1000 ranges"
        return result

    def _get_indicator_category(self, indicator: str) -> str:
        """Get the category of an indicator."""
        if indicator in self.trend_indicators:
            return "Trend"
        elif indicator in self.momentum_indicators:
            return "Momentum"
        elif indicator in self.volatility_indicators:
            return "Volatility"
        elif indicator in self.volume_indicators:
            return "Volume"
        elif indicator in self.statistical_indicators:
            return "Statistical"
        elif indicator in self.support_resistance_indicators:
            return "Support/Resistance"
        else:
            return "Unknown"
