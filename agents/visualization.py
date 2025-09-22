import json
import os
from typing import Any, Dict, List, Optional, Union
import numpy as np

from agno.tools import Toolkit
from agno.utils.log import log_info, logger
import matplotlib.pyplot as plt

class VisualizationTools(Toolkit):
    def __init__(
        self,
        bar_chart: bool = True,
        line_chart: bool = True,
        pie_chart: bool = True,
        scatter_plot: bool = True,
        histogram: bool = True,
        # New interactive chart types
        interactive_charts: bool = True,
        treemap: bool = True,
        sunburst: bool = True,
        heatmap: bool = True,
        enable_all: bool = False,
        output_dir: str = "charts",
        default_theme: str = "dark",
        **kwargs,
    ):
        """
        Initialize the VisualizationTools toolkit with enhanced styling, dark theme support, and interactive charts.

        Args:
            bar_chart (bool): Enable bar chart creation. Default is True.
            line_chart (bool): Enable line chart creation. Default is True.
            pie_chart (bool): Enable pie chart creation. Default is True.
            scatter_plot (bool): Enable scatter plot creation. Default is True.
            histogram (bool): Enable histogram creation. Default is True.
            enable_all (bool): Enable all chart types. Default is False.
            output_dir (str): Directory to save charts. Default is "charts".
        """
        super().__init__(**kwargs)

        # Check if matplotlib is available
        try:
            import matplotlib
            import matplotlib.pyplot as plt
            from matplotlib.colors import LinearSegmentedColormap
            import seaborn as sns
            
            # Use non-interactive backend to avoid display issues
            matplotlib.use("Agg")
            
            # Set modern style
            plt.style.use('seaborn-v0_8-darkgrid')
            sns.set_palette("husl")
            
        except ImportError:
            raise ImportError("matplotlib and seaborn are not installed. Please install them using: `pip install matplotlib seaborn`")

        # Check if plotly is available for interactive charts
        self.plotly_available = False
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            self.plotly_available = True
        except ImportError:
            logger.warning("Plotly not installed. Interactive charts will be disabled. Install with: `pip install plotly kaleido`")

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.output_dir = output_dir
        self.default_theme = default_theme
        
        # Define attractive color palettes for light theme
        self.color_palettes = {
            'vibrant': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8'],
            'professional': ['#2C3E50', '#3498DB', '#E74C3C', '#F39C12', '#27AE60', '#9B59B6', '#1ABC9C'],
            'sunset': ['#FF9472', '#F8B500', '#FFD23F', '#06FFA5', '#B4E7CE', '#C3AED6', '#8A2387'],
            'ocean': ['#667eea', '#764ba2', '#6B73FF', '#9068BE', '#495aff', '#0093E9', '#80D0C7'],
            'forest': ['#56ab2f', '#a8edea', '#fed6e3', '#ff9a9e', '#fad0c4', '#ffd1ff', '#c471f5']
        }
        
        # Enhanced dark theme color palettes for more creativity
        self.dark_color_palettes = {
            'neon': ['#FF073A', '#00F5FF', '#39FF14', '#FF1493', '#FFD700', '#DA70D6', '#00FFFF'],
            'cyberpunk': ['#00FFFF', '#FF006E', '#FFBE0B', '#8338EC', '#3A86FF', '#06FFA5', '#FB5607'],
            'aurora': ['#FF6B9D', '#C44569', '#F8B500', '#6C5CE7', '#74B9FF', '#00D2D3', '#FF7675'],
            'matrix': ['#00FF41', '#0080FF', '#FF0080', '#FFFF00', '#FF8000', '#8000FF', '#00FFFF'],
            'synthwave': ['#FF10F0', '#FF6EC7', '#C77DFF', '#7209B7', '#560BAD', '#480CA8', '#3A0CA3'],
            'electric': ['#FFFF00', '#00FFFF', '#FF1493', '#00FF00', '#FF4500', '#1E90FF', '#FF69B4'],
            'cosmic': ['#9D4EDD', '#7209B7', '#5A189A', '#240046', '#10002B', '#FF006E', '#FB8500'],
            'holographic': ['#FF00FF', '#00FFFF', '#FFFF00', '#FF4500', '#00FF00', '#8A2BE2', '#FF1493'],
            'galaxy': ['#4B0082', '#8A2BE2', '#9370DB', '#BA55D3', '#DA70D6', '#FF69B4', '#FF1493']
        }
        
        # Default gradient colors
        self.gradient_colors = ['#667eea', '#764ba2']

        # Register functions based on enabled chart types
        if enable_all:
            bar_chart = line_chart = pie_chart = scatter_plot = histogram = True
            interactive_charts = treemap = sunburst = heatmap = True

        if bar_chart:
            self.register(self.create_bar_chart)
        if line_chart:
            self.register(self.create_line_chart)
        if pie_chart:
            self.register(self.create_pie_chart)
        if scatter_plot:
            self.register(self.create_scatter_plot)
        if histogram:
            self.register(self.create_histogram)
            
        # Register new creative chart types
        if interactive_charts and self.plotly_available:
            self.register(self.create_interactive_bar_chart)
            self.register(self.create_interactive_line_chart)
            self.register(self.create_3d_scatter_plot)
        if treemap and self.plotly_available:
            self.register(self.create_treemap)
        if sunburst and self.plotly_available:
            self.register(self.create_sunburst_chart)
        if heatmap:
            self.register(self.create_heatmap)

    def _get_colors(self, n_colors: int, palette: str = 'vibrant', theme: str = 'light') -> List[str]:
        """Get n colors from the specified palette and theme."""
        if theme == 'dark':
            colors = self.dark_color_palettes.get(palette, self.dark_color_palettes['neon'])
        else:
            colors = self.color_palettes.get(palette, self.color_palettes['vibrant'])
        
        if n_colors <= len(colors):
            return colors[:n_colors]
        # Repeat colors if we need more
        return (colors * ((n_colors // len(colors)) + 1))[:n_colors]

    def _setup_modern_style(self, plt, theme: str = 'light'):
        """Apply modern styling to matplotlib with theme support."""
        if theme == 'dark':
            plt.rcParams.update({
                'font.size': 12,
                'font.family': 'sans-serif',
                'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
                'axes.titlesize': 16,
                'axes.titleweight': 'bold',
                'axes.labelsize': 12,
                'axes.labelweight': 'bold',
                'xtick.labelsize': 10,
                'ytick.labelsize': 10,
                'legend.fontsize': 11,
                'figure.titlesize': 18,
                'axes.spines.top': False,
                'axes.spines.right': False,
                'axes.grid': True,
                'grid.alpha': 0.3,
                'grid.linestyle': '--',
                'axes.axisbelow': True,
                'text.color': '#FFFFFF',
                'axes.labelcolor': '#FFFFFF',
                'xtick.color': '#FFFFFF',
                'ytick.color': '#FFFFFF',
                'axes.edgecolor': '#444444',
                'grid.color': '#444444'
            })
        else:
            plt.rcParams.update({
                'font.size': 12,
                'font.family': 'sans-serif',
                'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
                'axes.titlesize': 16,
                'axes.titleweight': 'bold',
                'axes.labelsize': 12,
                'axes.labelweight': 'bold',
                'xtick.labelsize': 10,
                'ytick.labelsize': 10,
                'legend.fontsize': 11,
                'figure.titlesize': 18,
                'axes.spines.top': False,
                'axes.spines.right': False,
                'axes.grid': True,
                'grid.alpha': 0.3,
                'grid.linestyle': '--',
                'axes.axisbelow': True
            })

    def _get_theme_colors(self, theme: str = 'light') -> Dict[str, str]:
        """Get theme-specific colors for backgrounds, text, etc."""
        if theme == 'dark':
            return {
                'bg_color': '#1A1A1A',
                'plot_bg': '#2D2D2D',
                'text_color': '#FFFFFF',
                'title_color': '#FFFFFF',
                'label_color': '#CCCCCC',
                'grid_color': '#444444',
                'edge_color': '#666666'
            }
        else:
            return {
                'bg_color': 'white',
                'plot_bg': '#FAFAFA',
                'text_color': '#2C3E50',
                'title_color': '#2C3E50',
                'label_color': '#34495E',
                'grid_color': 'gray',
                'edge_color': 'white'
            }

    def _normalize_data_for_charts(
        self, data: Union[Dict[str, Any], List[Dict[str, Any]], List[Any], str]
    ) -> Dict[str, Union[int, float]]:
        """
        Normalize various data formats into a simple dictionary format for charts.

        Args:
            data: Can be a dict, list of dicts, or list of values

        Returns:
            Dict with string keys and numeric values
        """
        if isinstance(data, dict):
            # Already in the right format, just ensure values are numeric
            return {str(k): float(v) if isinstance(v, (int, float)) else 0 for k, v in data.items()}

        elif isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                # List of dictionaries - try to find key-value pairs
                result = {}
                for item in data:
                    if isinstance(item, dict):
                        # Look for common key patterns
                        keys = list(item.keys())
                        if len(keys) >= 2:
                            # Use first key as label, second as value
                            label_key = keys[0]
                            value_key = keys[1]
                            result[str(item[label_key])] = (
                                float(item[value_key]) if isinstance(item[value_key], (int, float)) else 0
                            )
                return result
            else:
                # List of values - create numbered keys
                return {f"Item {i + 1}": float(v) if isinstance(v, (int, float)) else 0 for i, v in enumerate(data)}

        # Fallback
        return {"Data": 1.0}

    def create_bar_chart(
        self,
        data: Union[Dict[str, Union[int, float]], List[Dict[str, Any]], str],
        title: str = "Bar Chart",
        x_label: str = "Categories",
        y_label: str = "Values",
        filename: Optional[str] = None,
        color_palette: str = 'neon',
        theme: str = None,
    ) -> str:
        """
        Create an attractive bar chart with modern styling and theme support.

        Args:
            data: Dictionary with categories as keys and values as numbers,
                  or list of dictionaries, or JSON string
            title (str): Title of the chart
            x_label (str): Label for x-axis
            y_label (str): Label for y-axis
            filename (Optional[str]): Custom filename for the chart image
            color_palette (str): Color palette for the chart
            theme (str): Theme for the chart ('light' or 'dark')

        Returns:
            str: JSON string with chart information and file path
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Handle string input (JSON)
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            # Normalize data format
            normalized_data = self._normalize_data_for_charts(data)

            # Prepare data
            categories = list(normalized_data.keys())
            values = list(normalized_data.values())
            
            # Get attractive colors and theme colors
            colors = self._get_colors(len(categories), color_palette, theme)
            theme_colors = self._get_theme_colors(theme)
            
            # Setup modern styling
            self._setup_modern_style(plt, theme)

            # Create the chart with enhanced styling
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create bars with theme-appropriate styling
            if theme == 'dark':
                bars = ax.bar(categories, values, color=colors, alpha=0.9, 
                             edgecolor=theme_colors['edge_color'], linewidth=1.5)
                # Add glow effect for dark theme
                for bar in bars:
                    bar.set_linewidth(2)
            else:
                bars = ax.bar(categories, values, color=colors, alpha=0.8, 
                             edgecolor='white', linewidth=2)
            
            # Enhance the title and labels with theme colors
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20, 
                        color=theme_colors['title_color'])
            ax.set_xlabel(x_label, fontsize=14, fontweight='bold', color=theme_colors['label_color'])
            ax.set_ylabel(y_label, fontsize=14, fontweight='bold', color=theme_colors['label_color'])
            
            # Better axis formatting for trading data - use new utility method
            self._format_trading_axis(ax, categories, values, theme_colors)
            
            # Add value labels using the new trading annotation method
            self._add_trading_annotations(ax, categories, values, theme_colors, 'bar')
            
            # Enhance grid with theme colors
            ax.grid(True, alpha=0.3, linestyle='--', color=theme_colors['grid_color'])
            ax.set_axisbelow(True)
            
            # Set background colors
            fig.patch.set_facecolor(theme_colors['bg_color'])
            ax.set_facecolor(theme_colors['plot_bg'])
            
            plt.tight_layout()

            # Save the chart
            if filename is None:
                filename = f"{theme}_bar_chart_{len(os.listdir(self.output_dir)) + 1}.png"

            file_path = os.path.join(self.output_dir, filename)
            plt.savefig(file_path, dpi=300, bbox_inches="tight", facecolor=theme_colors['bg_color'])
            plt.close()

            log_info(f"Attractive {theme} theme bar chart created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"{theme}_bar_chart",
                    "title": title,
                    "file_path": file_path,
                    "data_points": len(normalized_data),
                    "color_palette": color_palette,
                    "theme": theme,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating attractive bar chart: {str(e)}")
            return json.dumps({"chart_type": "bar_chart", "error": str(e), "status": "error"})

    def create_line_chart(
        self,
        data: Union[Dict[str, Union[int, float]], List[Dict[str, Any]], str],
        title: str = "Line Chart",
        x_label: str = "X-axis",
        y_label: str = "Y-axis",
        filename: Optional[str] = None,
        color_palette: str = 'cyberpunk',
        theme: str = None,
    ) -> str:
        """
        Create an attractive line chart with modern styling, gradients and theme support.

        Args:
            data: Dictionary with x-values as keys and y-values as numbers,
                  or list of dictionaries, or JSON string
            title (str): Title of the chart
            x_label (str): Label for x-axis
            y_label (str): Label for y-axis
            filename (Optional[str]): Custom filename for the chart image
            color_palette (str): Color palette for the chart
            theme (str): Theme for the chart ('light' or 'dark')

        Returns:
            str: JSON string with chart information and file path
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Handle string input (JSON)
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            # Normalize data format
            normalized_data = self._normalize_data_for_charts(data)

            # Prepare data
            x_values = list(normalized_data.keys())
            y_values = list(normalized_data.values())
            
            # Get colors and theme colors
            colors = self._get_colors(2, color_palette, theme)
            theme_colors = self._get_theme_colors(theme)
            
            # Setup modern styling
            self._setup_modern_style(plt, theme)

            # Create the chart with enhanced styling
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Plot the line with attractive styling
            if theme == 'dark':
                line = ax.plot(x_values, y_values, linewidth=3, 
                              color=colors[0], alpha=0.9, marker='o', 
                              markersize=8, markerfacecolor=colors[1], 
                              markeredgecolor=theme_colors['bg_color'], markeredgewidth=2,
                              label='Data')
                # Add glow effect for dark theme
                ax.fill_between(x_values, y_values, alpha=0.2, color=colors[0])
            else:
                line = ax.plot(x_values, y_values, linewidth=4, 
                              color=colors[0], alpha=0.8, marker='o', 
                              markersize=8, markerfacecolor=colors[1], 
                              markeredgecolor='white', markeredgewidth=2,
                              label='Data')
                ax.fill_between(x_values, y_values, alpha=0.3, color=colors[0])
            
            # Enhance the title and labels
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20, 
                        color=theme_colors['title_color'])
            ax.set_xlabel(x_label, fontsize=14, fontweight='bold', color=theme_colors['label_color'])
            ax.set_ylabel(y_label, fontsize=14, fontweight='bold', color=theme_colors['label_color'])
            
            # Better axis formatting for trading data
            self._format_trading_axis(ax, x_values, y_values, theme_colors)
            
            # Add value annotations using the new trading annotation method
            self._add_trading_annotations(ax, x_values, y_values, theme_colors, 'line')
            
            # Enhance grid
            ax.grid(True, alpha=0.3, linestyle='--', color=theme_colors['grid_color'])
            ax.set_axisbelow(True)
            
            # Set background colors
            fig.patch.set_facecolor(theme_colors['bg_color'])
            ax.set_facecolor(theme_colors['plot_bg'])
            
            plt.tight_layout()

            # Save the chart
            if filename is None:
                filename = f"{theme}_line_chart_{len(os.listdir(self.output_dir)) + 1}.png"

            file_path = os.path.join(self.output_dir, filename)
            plt.savefig(file_path, dpi=300, bbox_inches="tight", facecolor=theme_colors['bg_color'])
            plt.close()

            log_info(f"Attractive {theme} theme line chart created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"{theme}_line_chart",
                    "title": title,
                    "file_path": file_path,
                    "data_points": len(normalized_data),
                    "color_palette": color_palette,
                    "theme": theme,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating attractive line chart: {str(e)}")
            return json.dumps({"chart_type": "line_chart", "error": str(e), "status": "error"})

    def create_pie_chart(
        self,
        data: Union[Dict[str, Union[int, float]], List[Dict[str, Any]], str],
        title: str = "Pie Chart",
        filename: Optional[str] = None,
        color_palette: str = 'aurora',
        theme: str = None,
    ) -> str:
        """
        Create an attractive pie chart with modern styling, effects and theme support.

        Args:
            data: Dictionary with categories as keys and values as numbers,
                  or list of dictionaries, or JSON string
            title (str): Title of the chart
            filename (Optional[str]): Custom filename for the chart image
            color_palette (str): Color palette for the chart
            theme (str): Theme for the chart ('light' or 'dark')

        Returns:
            str: JSON string with chart information and file path
        """
        try:
            import matplotlib.pyplot as plt

            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Handle string input (JSON)
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            # Normalize data format
            normalized_data = self._normalize_data_for_charts(data)

            # Prepare data
            labels = list(normalized_data.keys())
            values = list(normalized_data.values())
            
            # Get colors and theme colors
            colors = self._get_colors(len(labels), color_palette, theme)
            theme_colors = self._get_theme_colors(theme)
            
            # Setup modern styling
            self._setup_modern_style(plt, theme)

            # Create the chart with enhanced styling
            fig, ax = plt.subplots(figsize=(12, 10))
            
            # Create exploded effect for the largest slice
            explode = [0.05 if v == max(values) else 0 for v in values]
            
            # Create pie chart with theme-appropriate styling
            if theme == 'dark':
                wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors,
                                                 autopct='%1.1f%%', startangle=90,
                                                 explode=explode, shadow=True,
                                                 textprops={'fontsize': 11, 'fontweight': 'bold', 'color': theme_colors['text_color']})
                # Enhanced styling for dark theme
                for wedge in wedges:
                    wedge.set_edgecolor(theme_colors['bg_color'])
                    wedge.set_linewidth(2)
            else:
                wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors,
                                                 autopct='%1.1f%%', startangle=90,
                                                 explode=explode, shadow=True,
                                                 textprops={'fontsize': 11, 'fontweight': 'bold'})
                for wedge in wedges:
                    wedge.set_edgecolor('white')
                    wedge.set_linewidth(3)
            
            # Enhance percentage text
            for autotext in autotexts:
                if theme == 'dark':
                    autotext.set_color('#000000')  # Black text for better contrast on colored slices
                else:
                    autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            # Enhance labels with theme colors
            for text in texts:
                text.set_fontsize(12)
                text.set_fontweight('bold')
                text.set_color(theme_colors['text_color'])
            
            # Enhance the title
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20, 
                        color=theme_colors['title_color'])
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            
            # Set background colors
            fig.patch.set_facecolor(theme_colors['bg_color'])
            
            plt.tight_layout()

            # Save the chart
            if filename is None:
                filename = f"{theme}_pie_chart_{len(os.listdir(self.output_dir)) + 1}.png"

            file_path = os.path.join(self.output_dir, filename)
            plt.savefig(file_path, dpi=300, bbox_inches="tight", facecolor=theme_colors['bg_color'])
            plt.close()

            log_info(f"Attractive {theme} theme pie chart created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"{theme}_pie_chart",
                    "title": title,
                    "file_path": file_path,
                    "data_points": len(normalized_data),
                    "color_palette": color_palette,
                    "theme": theme,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating attractive pie chart: {str(e)}")
            return json.dumps({"chart_type": "pie_chart", "error": str(e), "status": "error"})

    def create_scatter_plot(
        self,
        x_data: Optional[List[Union[int, float]]] = None,
        y_data: Optional[List[Union[int, float]]] = None,
        title: str = "Scatter Plot",
        x_label: str = "X-axis",
        y_label: str = "Y-axis",
        filename: Optional[str] = None,
        color_palette: str = 'matrix',
        theme: str = None,
        # Alternative parameter names that agents might use
        x: Optional[List[Union[int, float]]] = None,
        y: Optional[List[Union[int, float]]] = None,
        data: Optional[Union[List[List[Union[int, float]]], Dict[str, List[Union[int, float]]]]] = None,
    ) -> str:
        """
        Create an attractive scatter plot with modern styling, gradient effects and theme support.

        Args:
            x_data: List of x-values (can also use 'x' parameter)
            y_data: List of y-values (can also use 'y' parameter)
            title (str): Title of the chart
            x_label (str): Label for x-axis
            y_label (str): Label for y-axis
            filename (Optional[str]): Custom filename for the chart image
            color_palette (str): Color palette for the chart
            theme (str): Theme for the chart ('light' or 'dark')
            data: Alternative format - list of [x,y] pairs or dict with 'x' and 'y' keys

        Returns:
            str: JSON string with chart information and file path
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Handle different parameter formats
            if x_data is None:
                x_data = x
            if y_data is None:
                y_data = y

            # Handle data parameter
            if data is not None:
                if isinstance(data, dict):
                    if "x" in data and "y" in data:
                        x_data = data["x"]
                        y_data = data["y"]
                elif isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], list) and len(data[0]) == 2:
                        x_data = [point[0] for point in data]
                        y_data = [point[1] for point in data]

            # Validate that we have data
            if x_data is None or y_data is None:
                raise ValueError("Missing x_data and y_data parameters")

            if len(x_data) != len(y_data):
                raise ValueError("x_data and y_data must have the same length")

            # Get colors and theme colors
            colors = self._get_colors(len(x_data), color_palette, theme)
            theme_colors = self._get_theme_colors(theme)
            
            # Setup modern styling
            self._setup_modern_style(plt, theme)

            # Create the chart with enhanced styling
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create scatter plot with theme-appropriate styling
            sizes = np.random.uniform(50, 200, len(x_data))
            if theme == 'dark':
                scatter = ax.scatter(x_data, y_data, c=colors[:len(x_data)], 
                                   s=sizes, alpha=0.8, edgecolors=theme_colors['bg_color'], 
                                   linewidth=1.5)
            else:
                scatter = ax.scatter(x_data, y_data, c=colors[:len(x_data)], 
                                   s=sizes, alpha=0.7, edgecolors='white', 
                                   linewidth=2)
            
            # Enhance the title and labels
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20, 
                        color=theme_colors['title_color'])
            ax.set_xlabel(x_label, fontsize=14, fontweight='bold', color=theme_colors['label_color'])
            ax.set_ylabel(y_label, fontsize=14, fontweight='bold', color=theme_colors['label_color'])
            
            plt.xticks(fontsize=11, color=theme_colors['text_color'])
            plt.yticks(fontsize=11, color=theme_colors['text_color'])
            
            # Enhance grid
            ax.grid(True, alpha=0.3, linestyle='--', color=theme_colors['grid_color'])
            ax.set_axisbelow(True)
            
            # Set background colors
            fig.patch.set_facecolor(theme_colors['bg_color'])
            ax.set_facecolor(theme_colors['plot_bg'])
            
            plt.tight_layout()

            # Save the chart
            if filename is None:
                filename = f"{theme}_scatter_plot_{len(os.listdir(self.output_dir)) + 1}.png"

            file_path = os.path.join(self.output_dir, filename)
            plt.savefig(file_path, dpi=300, bbox_inches="tight", facecolor=theme_colors['bg_color'])
            plt.close()

            log_info(f"Attractive {theme} theme scatter plot created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"{theme}_scatter_plot",
                    "title": title,
                    "file_path": file_path,
                    "data_points": len(x_data),
                    "color_palette": color_palette,
                    "theme": theme,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating attractive scatter plot: {str(e)}")
            return json.dumps({"chart_type": "scatter_plot", "error": str(e), "status": "error"})

    def create_histogram(
        self,
        data: List[Union[int, float]],
        bins: int = 10,
        title: str = "Histogram",
        x_label: str = "Values",
        y_label: str = "Frequency",
        filename: Optional[str] = None,
        color_palette: str = 'synthwave',
        theme: str = None,
    ) -> str:
        """
        Create an attractive histogram with modern styling, gradient effects and theme support.

        Args:
            data: List of numeric values to plot
            bins (int): Number of bins for the histogram
            title (str): Title of the chart
            x_label (str): Label for x-axis
            y_label (str): Label for y-axis
            filename (Optional[str]): Custom filename for the chart image
            color_palette (str): Color palette for the chart
            theme (str): Theme for the chart ('light' or 'dark')

        Returns:
            str: JSON string with chart information and file path
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Validate data
            if not isinstance(data, list) or len(data) == 0:
                raise ValueError("Data must be a non-empty list of numbers")

            # Convert to numeric values
            numeric_data = []
            for value in data:
                try:
                    numeric_data.append(float(value))
                except (ValueError, TypeError):
                    continue

            if len(numeric_data) == 0:
                raise ValueError("No valid numeric data found")

            # Get colors and theme colors
            colors = self._get_colors(bins, color_palette, theme)
            theme_colors = self._get_theme_colors(theme)
            
            # Setup modern styling
            self._setup_modern_style(plt, theme)

            # Create the chart with enhanced styling
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create histogram with theme-appropriate styling
            if theme == 'dark':
                n, bins_edges, patches = ax.hist(numeric_data, bins=bins, alpha=0.9, 
                                                edgecolor=theme_colors['bg_color'], linewidth=1.5)
            else:
                n, bins_edges, patches = ax.hist(numeric_data, bins=bins, alpha=0.8, 
                                                edgecolor='white', linewidth=2)
            
            # Apply gradient colors to bars
            for patch, color in zip(patches, colors[:len(patches)]):
                patch.set_facecolor(color)
                if theme == 'dark':
                    patch.set_edgecolor(theme_colors['bg_color'])
                    patch.set_linewidth(1.5)
                else:
                    patch.set_edgecolor('white')
                    patch.set_linewidth(2)
            
            # Enhance the title and labels
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20, 
                        color=theme_colors['title_color'])
            ax.set_xlabel(x_label, fontsize=14, fontweight='bold', color=theme_colors['label_color'])
            ax.set_ylabel(y_label, fontsize=14, fontweight='bold', color=theme_colors['label_color'])
            
            plt.xticks(fontsize=11, color=theme_colors['text_color'])
            plt.yticks(fontsize=11, color=theme_colors['text_color'])
            
            # Add frequency labels on top of bars
            for i, (patch, count) in enumerate(zip(patches, n)):
                if count > 0:
                    height = patch.get_height()
                    ax.text(patch.get_x() + patch.get_width()/2., height + max(n)*0.01,
                           f'{int(count)}', ha='center', va='bottom', 
                           fontweight='bold', fontsize=10, color=theme_colors['text_color'])
            
            # Enhance grid
            ax.grid(True, alpha=0.3, linestyle='--', color=theme_colors['grid_color'])
            ax.set_axisbelow(True)
            
            # Set background colors
            fig.patch.set_facecolor(theme_colors['bg_color'])
            ax.set_facecolor(theme_colors['plot_bg'])
            
            plt.tight_layout()

            # Save the chart
            if filename is None:
                filename = f"{theme}_histogram_{len(os.listdir(self.output_dir)) + 1}.png"

            file_path = os.path.join(self.output_dir, filename)
            plt.savefig(file_path, dpi=300, bbox_inches="tight", facecolor=theme_colors['bg_color'])
            plt.close()

            log_info(f"Attractive {theme} theme histogram created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"{theme}_histogram",
                    "title": title,
                    "file_path": file_path,
                    "data_points": len(numeric_data),
                    "bins": bins,
                    "color_palette": color_palette,
                    "theme": theme,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating attractive histogram: {str(e)}")
            return json.dumps({"chart_type": "histogram", "error": str(e), "status": "error"})

    def create_interactive_bar_chart(
        self,
        data: Union[Dict[str, Union[int, float]], List[Dict[str, Any]], str],
        title: str = "Interactive Bar Chart",
        x_label: str = "Categories",
        y_label: str = "Values",
        filename: Optional[str] = None,
        color_palette: str = 'holographic',
        theme: str = None,
    ) -> str:
        """
        Create a stunning interactive bar chart using Plotly.

        Args:
            data: Dictionary with categories as keys and values as numbers,
                  or list of dictionaries, or JSON string
            title (str): Title of the chart
            x_label (str): Label for x-axis
            y_label (str): Label for y-axis
            filename (Optional[str]): Custom filename for the chart image
            color_palette (str): Color palette for the chart
            theme (str): Theme for the chart ('light' or 'dark')

        Returns:
            str: JSON string with chart information and file path
        """
        try:
            if not self.plotly_available:
                return json.dumps({"error": "Plotly not available", "status": "error"})
                
            import plotly.graph_objects as go
            import plotly.express as px

            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Handle string input (JSON)
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            # Normalize data format
            normalized_data = self._normalize_data_for_charts(data)

            # Prepare data
            categories = list(normalized_data.keys())
            values = list(normalized_data.values())
            
            # Get attractive colors
            colors = self._get_colors(len(categories), color_palette, theme)

            # Create interactive bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker=dict(
                        color=colors,
                        line=dict(color='rgba(255,255,255,0.8)', width=2),
                        opacity=0.8
                    ),
                    text=values,
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
                )
            ])

            # Apply theme
            if theme == 'dark':
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#1A1A1A',
                    plot_bgcolor='#2D2D2D',
                )
            else:
                fig.update_layout(template='plotly_white')

            # Update layout
            fig.update_layout(
                title=dict(text=title, font=dict(size=20, color='white' if theme == 'dark' else 'black')),
                xaxis_title=x_label,
                yaxis_title=y_label,
                font=dict(size=12),
                showlegend=False,
                height=600,
                width=1000
            )

            # Save the chart
            if filename is None:
                filename = f"interactive_{theme}_bar_chart_{len(os.listdir(self.output_dir)) + 1}.html"

            file_path = os.path.join(self.output_dir, filename)
            fig.write_html(file_path)
            
            # Also save as PNG
            png_filename = filename.replace('.html', '.png')
            png_path = os.path.join(self.output_dir, png_filename)
            fig.write_image(png_path, width=1000, height=600, scale=2)

            log_info(f"Interactive bar chart created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"interactive_{theme}_bar_chart",
                    "title": title,
                    "file_path": file_path,
                    "png_path": png_path,
                    "data_points": len(normalized_data),
                    "color_palette": color_palette,
                    "theme": theme,
                    "interactive": True,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating interactive bar chart: {str(e)}")
            return json.dumps({"chart_type": "interactive_bar_chart", "error": str(e), "status": "error"})

    def create_interactive_line_chart(
        self,
        data: Union[Dict[str, Union[int, float]], List[Dict[str, Any]], str],
        title: str = "Interactive Line Chart",
        x_label: str = "X-axis",
        y_label: str = "Y-axis",
        filename: Optional[str] = None,
        color_palette: str = 'cyberpunk',
        theme: str = None,
    ) -> str:
        """
        Create a stunning interactive line chart using Plotly.

        Args:
            data: Dictionary with x-values as keys and y-values as numbers,
                  or list of dictionaries, or JSON string
            title (str): Title of the chart
            x_label (str): Label for x-axis
            y_label (str): Label for y-axis
            filename (Optional[str]): Custom filename for the chart image
            color_palette (str): Color palette for the chart
            theme (str): Theme for the chart ('light' or 'dark')

        Returns:
            str: JSON string with chart information and file path
        """
        try:
            if not self.plotly_available:
                return json.dumps({"error": "Plotly not available", "status": "error"})
                
            import plotly.graph_objects as go
            import plotly.express as px

            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Handle string input (JSON)
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            # Normalize data format
            normalized_data = self._normalize_data_for_charts(data)

            # Prepare data
            x_values = list(normalized_data.keys())
            y_values = list(normalized_data.values())
            
            # Get colors and theme colors
            colors = self._get_colors(2, color_palette, theme)
            theme_colors = self._get_theme_colors(theme)
            
            # Create interactive line chart
            fig = go.Figure(data=[
                go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode='lines+markers',
                    line=dict(color=colors[0], width=2),
                    marker=dict(size=8, color=colors[1], line=dict(width=2, color='white')),
                    text=y_values,
                    hovertemplate='<b>Value</b>: %{y}<br><b>X</b>: %{x}<extra></extra>'
                )
            ])

            # Apply theme
            if theme == 'dark':
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#1A1A1A',
                    plot_bgcolor='#2D2D2D',
                )
            else:
                fig.update_layout(template='plotly_white')

            # Update layout
            fig.update_layout(
                title=dict(text=title, font=dict(size=20, color='white' if theme == 'dark' else 'black')),
                xaxis_title=x_label,
                yaxis_title=y_label,
                font=dict(size=12),
                showlegend=False,
                height=600,
                width=1000
            )

            # Save the chart
            if filename is None:
                filename = f"interactive_{theme}_line_chart_{len(os.listdir(self.output_dir)) + 1}.html"

            file_path = os.path.join(self.output_dir, filename)
            fig.write_html(file_path)
            
            # Also save as PNG
            png_filename = filename.replace('.html', '.png')
            png_path = os.path.join(self.output_dir, png_filename)
            fig.write_image(png_path, width=1000, height=600, scale=2)

            log_info(f"Interactive line chart created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"interactive_{theme}_line_chart",
                    "title": title,
                    "file_path": file_path,
                    "png_path": png_path,
                    "data_points": len(normalized_data),
                    "color_palette": color_palette,
                    "theme": theme,
                    "interactive": True,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating interactive line chart: {str(e)}")
            return json.dumps({"chart_type": "interactive_line_chart", "error": str(e), "status": "error"})

    def create_3d_scatter_plot(
        self,
        x_data: List[Union[int, float]],
        y_data: List[Union[int, float]], 
        z_data: List[Union[int, float]],
        title: str = "3D Scatter Plot",
        x_label: str = "X-axis",
        y_label: str = "Y-axis",
        z_label: str = "Z-axis",
        filename: Optional[str] = None,
        color_palette: str = 'galaxy',
        theme: str = None,
    ) -> str:
        """
        Create a stunning 3D scatter plot using Plotly.

        Args:
            x_data: List of x-values (can also use 'x' parameter)
            y_data: List of y-values (can also use 'y' parameter)
            z_data: List of z-values
            title (str): Title of the chart
            x_label (str): Label for x-axis
            y_label (str): Label for y-axis
            z_label (str): Label for z-axis
            filename (Optional[str]): Custom filename for the chart image
            color_palette (str): Color palette for the chart
            theme (str): Theme for the chart ('light' or 'dark')

        Returns:
            str: JSON string with chart information and file path
        """
        try:
            if not self.plotly_available:
                return json.dumps({"error": "Plotly not available", "status": "error"})
                
            import plotly.graph_objects as go

            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Validate data
            if len(x_data) != len(y_data) or len(y_data) != len(z_data):
                raise ValueError("x_data, y_data, and z_data must have the same length")

            # Get attractive colors
            colors = self._get_colors(len(x_data), color_palette, theme)

            # Create 3D scatter plot
            fig = go.Figure(data=[go.Scatter3d(
                x=x_data,
                y=y_data,
                z=z_data,
                mode='markers',
                marker=dict(
                    size=8,
                    color=colors[:len(x_data)],
                    opacity=0.8,
                    line=dict(color='white', width=1)
                ),
                hovertemplate='<b>Point</b><br>X: %{x}<br>Y: %{y}<br>Z: %{z}<extra></extra>'
            )])

            # Apply theme
            if theme == 'dark':
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#1A1A1A',
                    scene=dict(
                        bgcolor='#2D2D2D',
                        xaxis=dict(gridcolor='#444444', showbackground=True, backgroundcolor='#2D2D2D'),
                        yaxis=dict(gridcolor='#444444', showbackground=True, backgroundcolor='#2D2D2D'),
                        zaxis=dict(gridcolor='#444444', showbackground=True, backgroundcolor='#2D2D2D')
                    )
                )

            # Update layout
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                scene=dict(
                    xaxis_title=x_label,
                    yaxis_title=y_label,
                    zaxis_title=z_label,
                ),
                height=700,
                width=1000
            )

            # Save the chart
            if filename is None:
                filename = f"3d_scatter_{theme}_{len(os.listdir(self.output_dir)) + 1}.html"

            file_path = os.path.join(self.output_dir, filename)
            fig.write_html(file_path)
            
            # Also save as PNG
            png_filename = filename.replace('.html', '.png')
            png_path = os.path.join(self.output_dir, png_filename)
            fig.write_image(png_path, width=1000, height=700, scale=2)

            log_info(f"3D scatter plot created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"3d_scatter_{theme}",
                    "title": title,
                    "file_path": file_path,
                    "png_path": png_path,
                    "data_points": len(x_data),
                    "color_palette": color_palette,
                    "theme": theme,
                    "interactive": True,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating 3D scatter plot: {str(e)}")
            return json.dumps({"chart_type": "3d_scatter", "error": str(e), "status": "error"})

    def create_treemap(
        self,
        data: Union[Dict[str, Union[int, float]], List[Dict[str, Any]], str],
        title: str = "Treemap",
        filename: Optional[str] = None,
        color_palette: str = 'cosmic',
        theme: str = None,
    ) -> str:
        """
        Create a beautiful treemap visualization using Plotly.

        Args:
            data: Dictionary with categories as keys and values as numbers,
                  or list of dictionaries, or JSON string
            title (str): Title of the chart
            filename (Optional[str]): Custom filename for the chart image
            color_palette (str): Color palette for the chart
            theme (str): Theme for the chart ('light' or 'dark')

        Returns:
            str: JSON string with chart information and file path
        """
        try:
            if not self.plotly_available:
                return json.dumps({"error": "Plotly not available", "status": "error"})
                
            import plotly.graph_objects as go

            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Handle string input (JSON)
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            # Normalize data format
            normalized_data = self._normalize_data_for_charts(data)

            # Prepare data
            labels = list(normalized_data.keys())
            values = list(normalized_data.values())
            
            # Get attractive colors
            colors = self._get_colors(len(labels), color_palette, theme)

            # Create treemap
            fig = go.Figure(go.Treemap(
                labels=labels,
                values=values,
                parents=[""] * len(labels),
                marker=dict(
                    colors=colors,
                    line=dict(width=2, color='white' if theme == 'light' else '#1A1A1A')
                ),
                textinfo="label+value+percent parent",
                textfont=dict(size=12, color='white' if theme == 'dark' else 'black'),
                hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percentParent}<extra></extra>'
            ))

            # Apply theme
            if theme == 'dark':
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#1A1A1A',
                )

            # Update layout
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                height=600,
                width=1000
            )

            # Save the chart
            if filename is None:
                filename = f"treemap_{theme}_{len(os.listdir(self.output_dir)) + 1}.html"

            file_path = os.path.join(self.output_dir, filename)
            fig.write_html(file_path)
            
            # Also save as PNG
            png_filename = filename.replace('.html', '.png')
            png_path = os.path.join(self.output_dir, png_filename)
            fig.write_image(png_path, width=1000, height=600, scale=2)

            log_info(f"Treemap created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"treemap_{theme}",
                    "title": title,
                    "file_path": file_path,
                    "png_path": png_path,
                    "data_points": len(normalized_data),
                    "color_palette": color_palette,
                    "theme": theme,
                    "interactive": True,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating treemap: {str(e)}")
            return json.dumps({"chart_type": "treemap", "error": str(e), "status": "error"})

    def create_sunburst_chart(
        self,
        data: List[Dict[str, Any]],
        title: str = "Sunburst Chart",
        filename: Optional[str] = None,
        color_palette: str = 'aurora',
        theme: str = None,
    ) -> str:
        """
        Create a stunning sunburst chart using Plotly.
        Expected data format: [{"id": "A", "parent": "", "value": 10}, {"id": "B", "parent": "A", "value": 5}]
        """
        try:
            if not self.plotly_available:
                return json.dumps({"error": "Plotly not available", "status": "error"})
                
            import plotly.graph_objects as go

            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Extract data
            ids = [item.get('id', f'Item_{i}') for i, item in enumerate(data)]
            parents = [item.get('parent', '') for item in data]
            values = [item.get('value', 1) for item in data]
            
            # Get attractive colors
            colors = self._get_colors(len(ids), color_palette, theme)

            # Create sunburst chart
            fig = go.Figure(go.Sunburst(
                ids=ids,
                labels=ids,
                parents=parents,
                values=values,
                branchvalues="total",
                marker=dict(
                    colors=colors,
                    line=dict(color='white' if theme == 'light' else '#1A1A1A', width=2)
                ),
                hovertemplate='<b>%{label}</b><br>Value: %{value}<extra></extra>'
            ))

            # Apply theme
            if theme == 'dark':
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='#1A1A1A',
                )

            # Update layout
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                height=600,
                width=600
            )

            # Save the chart
            if filename is None:
                filename = f"sunburst_{theme}_{len(os.listdir(self.output_dir)) + 1}.html"

            file_path = os.path.join(self.output_dir, filename)
            fig.write_html(file_path)
            
            # Also save as PNG
            png_filename = filename.replace('.html', '.png')
            png_path = os.path.join(self.output_dir, png_filename)
            fig.write_image(png_path, width=600, height=600, scale=2)

            log_info(f"Sunburst chart created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"sunburst_{theme}",
                    "title": title,
                    "file_path": file_path,
                    "png_path": png_path,
                    "data_points": len(data),
                    "color_palette": color_palette,
                    "theme": theme,
                    "interactive": True,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating sunburst chart: {str(e)}")
            return json.dumps({"chart_type": "sunburst", "error": str(e), "status": "error"})

    def create_heatmap(
        self,
        data: List[List[Union[int, float]]],
        x_labels: Optional[List[str]] = None,
        y_labels: Optional[List[str]] = None,
        title: str = "Heatmap",
        filename: Optional[str] = None,
        color_palette: str = 'synthwave',
        theme: str = None,
    ) -> str:
        """
        Create a beautiful heatmap using matplotlib with enhanced styling.

        Args:
            data: List of numeric values to plot
            x_labels: Optional list of labels for x-axis
            y_labels: Optional list of labels for y-axis
            title (str): Title of the chart
            filename (Optional[str]): Custom filename for the chart image
            color_palette (str): Color palette for the chart
            theme (str): Theme for the chart ('light' or 'dark')

        Returns:
            str: JSON string with chart information and file path
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Use default theme if not specified
            if theme is None:
                theme = self.default_theme

            # Convert data to numpy array
            data_array = np.array(data)
            
            # Get theme colors
            theme_colors = self._get_theme_colors(theme)
            
            # Setup modern styling
            self._setup_modern_style(plt, theme)

            # Create the heatmap
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Choose colormap based on theme
            if theme == 'dark':
                cmap = 'plasma'  # Vibrant colors for dark theme
            else:
                cmap = 'viridis'
            
            # Create heatmap
            im = ax.imshow(data_array, cmap=cmap, aspect='auto')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.ax.tick_params(labelsize=10, colors=theme_colors['text_color'])
            
            # Set labels
            if x_labels:
                ax.set_xticks(np.arange(len(x_labels)))
                ax.set_xticklabels(x_labels, rotation=45, ha="right")
            if y_labels:
                ax.set_yticks(np.arange(len(y_labels)))
                ax.set_yticklabels(y_labels)
            
            # Add text annotations
            for i in range(len(data)):
                for j in range(len(data[i])):
                    text = ax.text(j, i, f'{data[i][j]:.1f}',
                                 ha="center", va="center", color="white", fontweight="bold")

            # Enhance the title
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20, 
                        color=theme_colors['title_color'])
            
            # Style ticks
            plt.xticks(fontsize=11, color=theme_colors['text_color'])
            plt.yticks(fontsize=11, color=theme_colors['text_color'])
            
            # Set background colors
            fig.patch.set_facecolor(theme_colors['bg_color'])
            ax.set_facecolor(theme_colors['plot_bg'])
            
            plt.tight_layout()

            # Save the chart
            if filename is None:
                filename = f"heatmap_{theme}_{len(os.listdir(self.output_dir)) + 1}.png"

            file_path = os.path.join(self.output_dir, filename)
            plt.savefig(file_path, dpi=300, bbox_inches="tight", facecolor=theme_colors['bg_color'])
            plt.close()

            log_info(f"Heatmap created and saved to {file_path}")

            return json.dumps(
                {
                    "chart_type": f"heatmap_{theme}",
                    "title": title,
                    "file_path": file_path,
                    "data_points": len(data) * len(data[0]) if data else 0,
                    "color_palette": color_palette,
                    "theme": theme,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Error creating heatmap: {str(e)}")
            return json.dumps({"chart_type": "heatmap", "error": str(e), "status": "error"})

    def _format_trading_axis(self, ax, x_values, y_values, theme_colors):
        """Format axis specifically for trading data with better spacing and visibility."""
        # Smart x-axis label formatting
        if len(x_values) > 20:
            # For very large datasets, show every 5th label
            step = max(1, len(x_values) // 8)
        elif len(x_values) > 10:
            # For medium datasets, show every 3rd label
            step = max(1, len(x_values) // 6)
        else:
            # For small datasets, show all labels
            step = 1
        
        if step > 1:
            tick_positions = list(range(0, len(x_values), step))
            # Always include the last point for trading data
            if len(x_values) - 1 not in tick_positions:
                tick_positions.append(len(x_values) - 1)
            
            tick_labels = [str(x_values[i]) for i in tick_positions]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=10, 
                             color=theme_colors['text_color'])
        else:
            ax.set_xticks(range(len(x_values)))
            ax.set_xticklabels([str(x) for x in x_values], rotation=45, ha="right", 
                             fontsize=10, color=theme_colors['text_color'])
        
        # Format y-axis for financial precision
        y_min, y_max = min(y_values), max(y_values)
        y_range = y_max - y_min
        
        # Determine decimal places based on value range
        if y_range > 1000:
            format_str = '{x:,.0f}'  # No decimals for large numbers
        elif y_range > 10:
            format_str = '{x:,.1f}'  # 1 decimal place
        else:
            format_str = '{x:,.2f}'  # 2 decimal places for precise values
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_str.format(x=x)))
        
        # Add padding to y-axis for better visibility
        y_padding = y_range * 0.1
        ax.set_ylim(y_min - y_padding, y_max + y_padding)
        
        return ax

    def _add_trading_annotations(self, ax, x_values, y_values, theme_colors, chart_type='line'):
        """Add value annotations optimized for trading charts."""
        # Only annotate key points to avoid clutter
        n_points = len(x_values)
        
        if n_points <= 5:
            # Show all points for small datasets
            indices = list(range(n_points))
        elif n_points <= 20:
            # Show every 3rd point for medium datasets
            indices = list(range(0, n_points, 3))
            if n_points - 1 not in indices:
                indices.append(n_points - 1)  # Always show last point
        else:
            # Show start, end, and a few key points for large datasets
            indices = [0, n_points // 4, n_points // 2, 3 * n_points // 4, n_points - 1]
        
        for i in indices:
            if i < len(x_values) and i < len(y_values):
                x, y = x_values[i], y_values[i]
                
                # Format value based on magnitude
                if abs(y) > 1000:
                    value_text = f'{y:,.0f}'
                elif abs(y) > 10:
                    value_text = f'{y:,.1f}'
                else:
                    value_text = f'{y:,.2f}'
                
                if chart_type == 'line':
                    ax.annotate(value_text, (i, y), textcoords="offset points", 
                               xytext=(0, 15), ha='center', fontsize=8, 
                               fontweight='bold', color=theme_colors['text_color'],
                               bbox=dict(boxstyle="round,pad=0.3", facecolor=theme_colors['plot_bg'], 
                                        edgecolor=theme_colors['text_color'], alpha=0.8))
                elif chart_type == 'bar':
                    ax.text(i, y + max(y_values) * 0.01, value_text,
                           ha='center', va='bottom', fontweight='bold', 
                           fontsize=8, color=theme_colors['text_color'])