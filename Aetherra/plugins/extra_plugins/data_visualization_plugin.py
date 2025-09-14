"""
Data Visualization Plugin - Advanced Charting and Statistical Analysis
Author: Aetherra Plugin System
Version: 1.0.0

This plugin provides comprehensive data visualization capabilities including:
- Multiple chart types (line, bar, scatter, heatmap, box plots, etc.)
- Statistical analysis and correlation matrices
- Interactive plotting with matplotlib, plotly, and seaborn
- Data import from CSV, Excel, JSON, and database sources
- Custom styling and theming options
- Export capabilities for reports and presentations
"""

import base64
import io
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-interactive backend
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import seaborn as sns

    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.offline as pyo
    from plotly.subplots import make_subplots

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import scipy.stats as stats
    from scipy.cluster.hierarchy import dendrogram, linkage

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import sqlalchemy

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class ChartConfig:
    """Chart configuration structure."""

    chart_type: str
    title: str
    x_column: str
    y_column: str
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    group_by: Optional[str] = None
    width: int = 800
    height: int = 600
    theme: str = "default"
    color_palette: str = "viridis"
    show_legend: bool = True
    show_grid: bool = True
    x_label: str = ""
    y_label: str = ""
    export_format: str = "png"


@dataclass
class StatisticalAnalysis:
    """Statistical analysis results structure."""

    summary_stats: Dict[str, Any]
    correlation_matrix: Optional[Dict[str, Any]] = None
    distribution_analysis: Optional[Dict[str, Any]] = None
    outlier_analysis: Optional[Dict[str, Any]] = None
    trend_analysis: Optional[Dict[str, Any]] = None


@dataclass
class VisualizationResult:
    """Visualization result structure."""

    chart_config: ChartConfig
    image_data: str  # Base64 encoded image
    html_content: Optional[str] = None  # For interactive charts
    statistical_analysis: Optional[StatisticalAnalysis] = None
    file_path: Optional[str] = None
    creation_date: str = ""
    data_summary: Dict[str, Any] = None


class DataProcessor:
    """Data processing and analysis utilities."""

    def __init__(self):
        self.supported_formats = ["csv", "xlsx", "json", "parquet"]

    def load_data(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Load data from various file formats."""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == ".csv":
                return pd.read_csv(file_path, **kwargs)
            elif file_ext in [".xlsx", ".xls"]:
                return pd.read_excel(file_path, **kwargs)
            elif file_ext == ".json":
                return pd.read_json(file_path, **kwargs)
            elif file_ext == ".parquet":
                return pd.read_parquet(file_path, **kwargs)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            raise

    def load_from_database(self, connection_string: str, query: str) -> pd.DataFrame:
        """Load data from database using SQL query."""
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required for database connections")

        try:
            engine = sqlalchemy.create_engine(connection_string)
            return pd.read_sql(query, engine)
        except Exception as e:
            logger.error(f"Error loading data from database: {e}")
            raise

    def clean_data(
        self,
        df: pd.DataFrame,
        remove_nulls: bool = True,
        remove_duplicates: bool = True,
        numeric_columns: List[str] = None,
    ) -> pd.DataFrame:
        """Clean and preprocess data."""
        df_clean = df.copy()

        if remove_nulls:
            df_clean = df_clean.dropna()

        if remove_duplicates:
            df_clean = df_clean.drop_duplicates()

        # Convert specified columns to numeric
        if numeric_columns:
            for col in numeric_columns:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

        return df_clean

    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive data summary."""
        summary = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "numeric_columns": list(df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": list(df.select_dtypes(include=["object"]).columns),
            "datetime_columns": list(df.select_dtypes(include=["datetime64"]).columns),
        }

        # Basic statistics for numeric columns
        if summary["numeric_columns"]:
            summary["statistics"] = df[summary["numeric_columns"]].describe().to_dict()

        return summary


class StatisticalAnalyzer:
    """Statistical analysis and testing utilities."""

    def __init__(self):
        self.available_tests = [
            "correlation",
            "regression",
            "t_test",
            "chi_square",
            "anova",
            "normality",
            "outliers",
            "clustering",
        ]

    def correlation_analysis(
        self, df: pd.DataFrame, columns: List[str] = None, method: str = "pearson"
    ) -> Dict[str, Any]:
        """Perform correlation analysis."""
        if columns is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        else:
            numeric_cols = [col for col in columns if col in df.columns]

        if len(numeric_cols) < 2:
            return {"error": "Need at least 2 numeric columns for correlation"}

        corr_matrix = df[numeric_cols].corr(method=method)

        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:  # Strong correlation threshold
                    strong_correlations.append(
                        {
                            "variable1": corr_matrix.columns[i],
                            "variable2": corr_matrix.columns[j],
                            "correlation": corr_val,
                            "strength": "strong" if abs(corr_val) > 0.8 else "moderate",
                        }
                    )

        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "method": method,
        }

    def distribution_analysis(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Analyze distribution of a column."""
        if column not in df.columns:
            return {"error": f"Column {column} not found"}

        series = df[column].dropna()

        if not pd.api.types.is_numeric_dtype(series):
            # Categorical distribution
            value_counts = series.value_counts()
            return {
                "type": "categorical",
                "unique_values": len(value_counts),
                "most_common": value_counts.head(10).to_dict(),
                "entropy": -(
                    value_counts / len(series) * np.log2(value_counts / len(series))
                ).sum(),
            }
        else:
            # Numerical distribution
            analysis = {
                "type": "numerical",
                "mean": series.mean(),
                "median": series.median(),
                "std": series.std(),
                "min": series.min(),
                "max": series.max(),
                "quartiles": series.quantile([0.25, 0.5, 0.75]).to_dict(),
                "skewness": series.skew(),
                "kurtosis": series.kurtosis(),
            }

            # Normality test if scipy available
            if SCIPY_AVAILABLE and len(series) > 3:
                try:
                    stat, p_value = stats.normaltest(series)
                    analysis["normality_test"] = {
                        "statistic": stat,
                        "p_value": p_value,
                        "is_normal": p_value > 0.05,
                    }
                except Exception:
                    pass

            return analysis

    def outlier_detection(
        self, df: pd.DataFrame, column: str, method: str = "iqr"
    ) -> Dict[str, Any]:
        """Detect outliers in a column."""
        if column not in df.columns:
            return {"error": f"Column {column} not found"}

        series = df[column].dropna()

        if not pd.api.types.is_numeric_dtype(series):
            return {"error": "Outlier detection only available for numeric columns"}

        if method == "iqr":
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = series[(series < lower_bound) | (series > upper_bound)]

            return {
                "method": "IQR",
                "outlier_count": len(outliers),
                "outlier_percentage": len(outliers) / len(series) * 100,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "outlier_values": outliers.tolist()[:50],  # Limit to first 50
            }
        elif method == "zscore":
            z_scores = np.abs(stats.zscore(series))
            outliers = series[z_scores > 3]

            return {
                "method": "Z-Score",
                "outlier_count": len(outliers),
                "outlier_percentage": len(outliers) / len(series) * 100,
                "threshold": 3,
                "outlier_values": outliers.tolist()[:50],
            }

    def trend_analysis(
        self, df: pd.DataFrame, x_column: str, y_column: str
    ) -> Dict[str, Any]:
        """Analyze trends between two variables."""
        if x_column not in df.columns or y_column not in df.columns:
            return {"error": "One or both columns not found"}

        # Remove rows with null values in either column
        clean_df = df[[x_column, y_column]].dropna()

        if len(clean_df) < 2:
            return {"error": "Not enough data points for trend analysis"}

        x_data = clean_df[x_column]
        y_data = clean_df[y_column]

        # Convert datetime to numeric if needed
        if pd.api.types.is_datetime64_any_dtype(x_data):
            x_numeric = pd.to_numeric(x_data)
        else:
            x_numeric = pd.to_numeric(x_data, errors="coerce")

        y_numeric = pd.to_numeric(y_data, errors="coerce")

        # Remove any remaining NaN values
        valid_mask = ~(np.isnan(x_numeric) | np.isnan(y_numeric))
        x_numeric = x_numeric[valid_mask]
        y_numeric = y_numeric[valid_mask]

        if len(x_numeric) < 2:
            return {"error": "Not enough valid numeric data for trend analysis"}

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            x_numeric, y_numeric
        )

        # Trend direction
        if slope > 0:
            trend_direction = "increasing"
        elif slope < 0:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value**2,
            "p_value": p_value,
            "std_error": std_err,
            "trend_direction": trend_direction,
            "trend_strength": "strong"
            if abs(r_value) > 0.7
            else "moderate"
            if abs(r_value) > 0.3
            else "weak",
        }


class ChartGenerator:
    """Chart generation using matplotlib and seaborn."""

    def __init__(self):
        self.figure_size = (10, 6)
        self.dpi = 100
        self.style = "default"

        # Set up matplotlib style
        if MATPLOTLIB_AVAILABLE:
            plt.style.use("default")

        # Set up seaborn style
        if SEABORN_AVAILABLE:
            sns.set_style("whitegrid")

    def create_line_chart(self, df: pd.DataFrame, config: ChartConfig) -> str:
        """Create line chart."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib is required for line charts")

        fig, ax = plt.subplots(
            figsize=(config.width / 100, config.height / 100), dpi=self.dpi
        )

        if config.group_by and config.group_by in df.columns:
            # Multiple lines grouped by category
            for group_name, group_df in df.groupby(config.group_by):
                ax.plot(
                    group_df[config.x_column],
                    group_df[config.y_column],
                    label=str(group_name),
                    marker="o",
                    markersize=4,
                )
        else:
            # Single line
            ax.plot(
                df[config.x_column],
                df[config.y_column],
                marker="o",
                markersize=4,
                linewidth=2,
            )

        ax.set_title(config.title, fontsize=14, fontweight="bold")
        ax.set_xlabel(config.x_label or config.x_column, fontsize=12)
        ax.set_ylabel(config.y_label or config.y_column, fontsize=12)

        if config.show_grid:
            ax.grid(True, alpha=0.3)

        if config.show_legend and config.group_by:
            ax.legend()

        plt.tight_layout()

        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(
            img_buffer, format=config.export_format, dpi=self.dpi, bbox_inches="tight"
        )
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)

        return img_base64

    def create_bar_chart(self, df: pd.DataFrame, config: ChartConfig) -> str:
        """Create bar chart."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib is required for bar charts")

        fig, ax = plt.subplots(
            figsize=(config.width / 100, config.height / 100), dpi=self.dpi
        )

        if config.group_by and config.group_by in df.columns:
            # Grouped bar chart
            df_pivot = df.pivot_table(
                values=config.y_column,
                index=config.x_column,
                columns=config.group_by,
                aggfunc="mean",
            )
            df_pivot.plot(kind="bar", ax=ax, width=0.8)
        else:
            # Simple bar chart
            if pd.api.types.is_numeric_dtype(df[config.x_column]):
                # If x is numeric, aggregate by bins
                x_data = df[config.x_column]
                y_data = df[config.y_column]
                ax.bar(range(len(x_data)), y_data, width=0.8)
                ax.set_xticks(range(len(x_data)))
                ax.set_xticklabels([str(x) for x in x_data], rotation=45)
            else:
                # Categorical x-axis
                df_agg = df.groupby(config.x_column)[config.y_column].mean()
                ax.bar(df_agg.index, df_agg.values, width=0.8)

        ax.set_title(config.title, fontsize=14, fontweight="bold")
        ax.set_xlabel(config.x_label or config.x_column, fontsize=12)
        ax.set_ylabel(config.y_label or config.y_column, fontsize=12)

        if config.show_grid:
            ax.grid(True, alpha=0.3, axis="y")

        if config.show_legend and config.group_by:
            ax.legend()

        plt.xticks(rotation=45)
        plt.tight_layout()

        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(
            img_buffer, format=config.export_format, dpi=self.dpi, bbox_inches="tight"
        )
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)

        return img_base64

    def create_scatter_plot(self, df: pd.DataFrame, config: ChartConfig) -> str:
        """Create scatter plot."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib is required for scatter plots")

        fig, ax = plt.subplots(
            figsize=(config.width / 100, config.height / 100), dpi=self.dpi
        )

        # Prepare data
        x_data = df[config.x_column]
        y_data = df[config.y_column]

        # Color and size mapping
        c = None
        s = 50  # Default size

        if config.color_column and config.color_column in df.columns:
            c = df[config.color_column]

        if config.size_column and config.size_column in df.columns:
            s = df[config.size_column]
            # Normalize sizes
            s = (s - s.min()) / (s.max() - s.min()) * 200 + 20

        scatter = ax.scatter(
            x_data, y_data, c=c, s=s, alpha=0.6, cmap=config.color_palette
        )

        if config.color_column and c is not None:
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label(config.color_column)

        ax.set_title(config.title, fontsize=14, fontweight="bold")
        ax.set_xlabel(config.x_label or config.x_column, fontsize=12)
        ax.set_ylabel(config.y_label or config.y_column, fontsize=12)

        if config.show_grid:
            ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(
            img_buffer, format=config.export_format, dpi=self.dpi, bbox_inches="tight"
        )
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)

        return img_base64

    def create_heatmap(self, df: pd.DataFrame, config: ChartConfig) -> str:
        """Create heatmap/correlation matrix."""
        if not SEABORN_AVAILABLE:
            raise ImportError("Seaborn is required for heatmaps")

        fig, ax = plt.subplots(
            figsize=(config.width / 100, config.height / 100), dpi=self.dpi
        )

        # If specific columns not provided, use correlation matrix of numeric columns
        if config.x_column == "correlation" or config.y_column == "correlation":
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            corr_matrix = df[numeric_cols].corr()
            sns.heatmap(
                corr_matrix,
                annot=True,
                cmap=config.color_palette,
                center=0,
                ax=ax,
                square=True,
                fmt=".2f",
            )
            ax.set_title(
                config.title or "Correlation Matrix", fontsize=14, fontweight="bold"
            )
        else:
            # Pivot table heatmap
            pivot_data = df.pivot_table(
                values=config.y_column,
                index=config.x_column,
                columns=config.group_by or config.color_column,
                aggfunc="mean",
            )
            sns.heatmap(
                pivot_data, annot=True, cmap=config.color_palette, ax=ax, fmt=".1f"
            )
            ax.set_title(config.title, fontsize=14, fontweight="bold")

        plt.tight_layout()

        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(
            img_buffer, format=config.export_format, dpi=self.dpi, bbox_inches="tight"
        )
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)

        return img_base64

    def create_box_plot(self, df: pd.DataFrame, config: ChartConfig) -> str:
        """Create box plot."""
        if not SEABORN_AVAILABLE:
            raise ImportError("Seaborn is required for box plots")

        fig, ax = plt.subplots(
            figsize=(config.width / 100, config.height / 100), dpi=self.dpi
        )

        if config.group_by and config.group_by in df.columns:
            sns.boxplot(
                data=df,
                x=config.x_column,
                y=config.y_column,
                hue=config.group_by,
                ax=ax,
                palette=config.color_palette,
            )
        else:
            sns.boxplot(
                data=df,
                x=config.x_column,
                y=config.y_column,
                ax=ax,
                palette=config.color_palette,
            )

        ax.set_title(config.title, fontsize=14, fontweight="bold")
        ax.set_xlabel(config.x_label or config.x_column, fontsize=12)
        ax.set_ylabel(config.y_label or config.y_column, fontsize=12)

        if config.show_grid:
            ax.grid(True, alpha=0.3, axis="y")

        plt.xticks(rotation=45)
        plt.tight_layout()

        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(
            img_buffer, format=config.export_format, dpi=self.dpi, bbox_inches="tight"
        )
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)

        return img_base64

    def create_histogram(self, df: pd.DataFrame, config: ChartConfig) -> str:
        """Create histogram."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib is required for histograms")

        fig, ax = plt.subplots(
            figsize=(config.width / 100, config.height / 100), dpi=self.dpi
        )

        if config.group_by and config.group_by in df.columns:
            # Multiple histograms
            for group_name, group_df in df.groupby(config.group_by):
                ax.hist(
                    group_df[config.x_column], alpha=0.7, label=str(group_name), bins=30
                )
        else:
            # Single histogram
            ax.hist(df[config.x_column], bins=30, alpha=0.7, edgecolor="black")

        ax.set_title(config.title, fontsize=14, fontweight="bold")
        ax.set_xlabel(config.x_label or config.x_column, fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)

        if config.show_grid:
            ax.grid(True, alpha=0.3, axis="y")

        if config.show_legend and config.group_by:
            ax.legend()

        plt.tight_layout()

        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(
            img_buffer, format=config.export_format, dpi=self.dpi, bbox_inches="tight"
        )
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)

        return img_base64


class InteractiveChartGenerator:
    """Interactive chart generation using Plotly."""

    def __init__(self):
        self.default_theme = "plotly_white"

    def create_interactive_scatter(self, df: pd.DataFrame, config: ChartConfig) -> str:
        """Create interactive scatter plot."""
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly is required for interactive charts")

        fig = px.scatter(
            df,
            x=config.x_column,
            y=config.y_column,
            color=config.color_column,
            size=config.size_column,
            title=config.title,
            color_continuous_scale=config.color_palette,
            width=config.width,
            height=config.height,
        )

        fig.update_layout(template=self.default_theme)
        fig.update_xaxes(title=config.x_label or config.x_column)
        fig.update_yaxes(title=config.y_label or config.y_column)

        return fig.to_html(include_plotlyjs="cdn")

    def create_interactive_line(self, df: pd.DataFrame, config: ChartConfig) -> str:
        """Create interactive line chart."""
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly is required for interactive charts")

        fig = px.line(
            df,
            x=config.x_column,
            y=config.y_column,
            color=config.group_by,
            title=config.title,
            width=config.width,
            height=config.height,
        )

        fig.update_layout(template=self.default_theme)
        fig.update_xaxes(title=config.x_label or config.x_column)
        fig.update_yaxes(title=config.y_label or config.y_column)

        return fig.to_html(include_plotlyjs="cdn")


class DataVisualizationPlugin:
    """Main Data Visualization Plugin class."""

    def __init__(self):
        self.name = "Data Visualization"
        self.version = "1.0.0"
        self.description = "Advanced data visualization and statistical analysis system"

        # Initialize components
        self.data_processor = DataProcessor()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.chart_generator = ChartGenerator()
        self.interactive_generator = InteractiveChartGenerator()

        # Plugin configuration
        self.config = {
            "output_directory": "visualizations",
            "default_chart_size": (800, 600),
            "default_dpi": 100,
            "supported_formats": ["png", "jpg", "svg", "pdf"],
            "auto_clean_data": True,
            "enable_statistical_analysis": True,
            "color_palettes": ["viridis", "plasma", "coolwarm", "Set1", "tab10"],
            "chart_themes": ["default", "seaborn", "ggplot", "bmh"],
        }

        # Ensure output directory exists
        os.makedirs(self.config["output_directory"], exist_ok=True)

    async def initialize(self):
        """Initialize the plugin."""
        logger.info("Data Visualization Plugin initialized")

    async def cleanup(self):
        """Cleanup plugin resources."""
        logger.info("Data Visualization Plugin cleaned up")

    def capabilities(self) -> List[str]:
        """Return plugin capabilities."""
        return [
            "data_loading",
            "data_cleaning",
            "statistical_analysis",
            "chart_generation",
            "interactive_visualization",
            "correlation_analysis",
            "trend_analysis",
            "outlier_detection",
            "export_capabilities",
        ]

    async def invoke(
        self, action: str, payload: Dict[str, Any], context=None
    ) -> Dict[str, Any]:
        """Main plugin invocation method."""
        try:
            if action == "load_data":
                return await self.load_data(
                    payload.get("file_path"), payload.get("options", {})
                )
            elif action == "create_chart":
                return await self.create_chart(
                    payload.get("data"), payload.get("config")
                )
            elif action == "analyze_data":
                return await self.analyze_data(
                    payload.get("data"),
                    payload.get("analysis_type"),
                    payload.get("options", {}),
                )
            elif action == "generate_dashboard":
                return await self.generate_dashboard(
                    payload.get("data"), payload.get("charts")
                )
            elif action == "export_visualization":
                return await self.export_visualization(
                    payload.get("visualization"),
                    payload.get("format"),
                    payload.get("file_path"),
                )
            elif action == "get_data_summary":
                return await self.get_data_summary(payload.get("data"))
            elif action == "get_config":
                return {"status": "success", "data": self.config}
            elif action == "update_config":
                return await self.update_config(payload)
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Plugin invocation failed: {e}")
            return {"status": "error", "message": str(e)}

    async def load_data(
        self, file_path: str, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Load data from file or database."""
        try:
            if not file_path:
                return {"status": "error", "message": "File path is required"}

            if file_path.startswith("sql://"):
                # Database connection
                connection_string = options.get("connection_string")
                query = options.get("query")
                if not connection_string or not query:
                    return {
                        "status": "error",
                        "message": "Database connection requires connection_string and query",
                    }
                df = self.data_processor.load_from_database(connection_string, query)
            else:
                # File loading
                df = self.data_processor.load_data(file_path, **options)

            # Clean data if requested
            if self.config["auto_clean_data"] and options.get("clean_data", True):
                df = self.data_processor.clean_data(
                    df,
                    remove_nulls=options.get("remove_nulls", True),
                    remove_duplicates=options.get("remove_duplicates", True),
                    numeric_columns=options.get("numeric_columns"),
                )

            # Get data summary
            summary = self.data_processor.get_data_summary(df)

            # Convert DataFrame to JSON for transport
            data_json = df.to_json(orient="records")

            return {
                "status": "success",
                "data": {
                    "dataframe": data_json,
                    "summary": summary,
                    "shape": df.shape,
                    "columns": list(df.columns),
                },
                "message": f"Loaded {df.shape[0]} rows and {df.shape[1]} columns",
            }

        except Exception as e:
            return {"status": "error", "message": f"Data loading failed: {e}"}

    async def create_chart(
        self, data: Union[str, Dict], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a chart from data."""
        try:
            # Parse data
            if isinstance(data, str):
                df = pd.read_json(data, orient="records")
            elif isinstance(data, dict) and "dataframe" in data:
                df = pd.read_json(data["dataframe"], orient="records")
            else:
                return {"status": "error", "message": "Invalid data format"}

            # Create chart config
            chart_config = ChartConfig(**config)

            # Generate chart based on type
            chart_type = chart_config.chart_type.lower()

            if chart_type == "line":
                image_data = self.chart_generator.create_line_chart(df, chart_config)
            elif chart_type == "bar":
                image_data = self.chart_generator.create_bar_chart(df, chart_config)
            elif chart_type == "scatter":
                image_data = self.chart_generator.create_scatter_plot(df, chart_config)
            elif chart_type == "heatmap":
                image_data = self.chart_generator.create_heatmap(df, chart_config)
            elif chart_type == "box":
                image_data = self.chart_generator.create_box_plot(df, chart_config)
            elif chart_type == "histogram":
                image_data = self.chart_generator.create_histogram(df, chart_config)
            elif chart_type in ["interactive_scatter", "interactive_line"]:
                html_content = getattr(
                    self.interactive_generator, f"create_{chart_type}"
                )(df, chart_config)
                image_data = ""  # No static image for interactive charts
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported chart type: {chart_type}",
                }

            # Statistical analysis if enabled
            statistical_analysis = None
            if self.config["enable_statistical_analysis"]:
                statistical_analysis = await self._perform_chart_analysis(
                    df, chart_config
                )

            # Create result
            result = VisualizationResult(
                chart_config=chart_config,
                image_data=image_data,
                html_content=html_content
                if chart_type.startswith("interactive")
                else None,
                statistical_analysis=statistical_analysis,
                creation_date=datetime.now().isoformat(),
                data_summary=self.data_processor.get_data_summary(df),
            )

            return {
                "status": "success",
                "data": asdict(result),
                "message": f"Chart created successfully: {chart_type}",
            }

        except Exception as e:
            return {"status": "error", "message": f"Chart creation failed: {e}"}

    async def analyze_data(
        self, data: Union[str, Dict], analysis_type: str, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform statistical analysis on data."""
        try:
            # Parse data
            if isinstance(data, str):
                df = pd.read_json(data, orient="records")
            elif isinstance(data, dict) and "dataframe" in data:
                df = pd.read_json(data["dataframe"], orient="records")
            else:
                return {"status": "error", "message": "Invalid data format"}

            analysis_results = {}

            if analysis_type == "correlation":
                analysis_results = self.statistical_analyzer.correlation_analysis(
                    df, options.get("columns"), options.get("method", "pearson")
                )
            elif analysis_type == "distribution":
                column = options.get("column")
                if not column:
                    return {
                        "status": "error",
                        "message": "Column required for distribution analysis",
                    }
                analysis_results = self.statistical_analyzer.distribution_analysis(
                    df, column
                )
            elif analysis_type == "outliers":
                column = options.get("column")
                method = options.get("method", "iqr")
                if not column:
                    return {
                        "status": "error",
                        "message": "Column required for outlier analysis",
                    }
                analysis_results = self.statistical_analyzer.outlier_detection(
                    df, column, method
                )
            elif analysis_type == "trend":
                x_col = options.get("x_column")
                y_col = options.get("y_column")
                if not x_col or not y_col:
                    return {
                        "status": "error",
                        "message": "Both x_column and y_column required for trend analysis",
                    }
                analysis_results = self.statistical_analyzer.trend_analysis(
                    df, x_col, y_col
                )
            elif analysis_type == "summary":
                analysis_results = self.data_processor.get_data_summary(df)
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported analysis type: {analysis_type}",
                }

            return {
                "status": "success",
                "data": {
                    "analysis_type": analysis_type,
                    "results": analysis_results,
                    "timestamp": datetime.now().isoformat(),
                },
                "message": f"Analysis completed: {analysis_type}",
            }

        except Exception as e:
            return {"status": "error", "message": f"Analysis failed: {e}"}

    async def generate_dashboard(
        self, data: Union[str, Dict], charts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate dashboard with multiple charts."""
        try:
            # Parse data
            if isinstance(data, str):
                df = pd.read_json(data, orient="records")
            elif isinstance(data, dict) and "dataframe" in data:
                df = pd.read_json(data["dataframe"], orient="records")
            else:
                return {"status": "error", "message": "Invalid data format"}

            dashboard_charts = []

            for chart_config in charts:
                result = await self.create_chart(
                    df.to_json(orient="records"), chart_config
                )
                if result["status"] == "success":
                    dashboard_charts.append(result["data"])

            dashboard_html = self._generate_dashboard_html(dashboard_charts)

            # Save dashboard
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dashboard_path = os.path.join(
                self.config["output_directory"], f"dashboard_{timestamp}.html"
            )

            with open(dashboard_path, "w", encoding="utf-8") as f:
                f.write(dashboard_html)

            return {
                "status": "success",
                "data": {
                    "dashboard_html": dashboard_html,
                    "dashboard_path": dashboard_path,
                    "charts": dashboard_charts,
                    "chart_count": len(dashboard_charts),
                },
                "message": f"Dashboard created with {len(dashboard_charts)} charts",
            }

        except Exception as e:
            return {"status": "error", "message": f"Dashboard generation failed: {e}"}

    async def export_visualization(
        self, visualization: Dict[str, Any], export_format: str, file_path: str
    ) -> Dict[str, Any]:
        """Export visualization to file."""
        try:
            if export_format.lower() in ["png", "jpg", "jpeg"]:
                # Export static image
                image_data = visualization.get("image_data")
                if not image_data:
                    return {"status": "error", "message": "No image data available"}

                # Decode base64 and save
                img_bytes = base64.b64decode(image_data)
                with open(file_path, "wb") as f:
                    f.write(img_bytes)

            elif export_format.lower() == "html":
                # Export HTML (for interactive charts)
                html_content = visualization.get("html_content")
                if not html_content:
                    return {"status": "error", "message": "No HTML content available"}

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

            elif export_format.lower() == "json":
                # Export configuration and data
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(visualization, f, indent=2, default=str)

            else:
                return {
                    "status": "error",
                    "message": f"Unsupported export format: {export_format}",
                }

            return {
                "status": "success",
                "data": {"file_path": file_path, "format": export_format},
                "message": f"Visualization exported to {file_path}",
            }

        except Exception as e:
            return {"status": "error", "message": f"Export failed: {e}"}

    async def get_data_summary(self, data: Union[str, Dict]) -> Dict[str, Any]:
        """Get comprehensive data summary."""
        try:
            # Parse data
            if isinstance(data, str):
                df = pd.read_json(data, orient="records")
            elif isinstance(data, dict) and "dataframe" in data:
                df = pd.read_json(data["dataframe"], orient="records")
            else:
                return {"status": "error", "message": "Invalid data format"}

            summary = self.data_processor.get_data_summary(df)

            return {
                "status": "success",
                "data": summary,
                "message": "Data summary generated",
            }

        except Exception as e:
            return {"status": "error", "message": f"Summary generation failed: {e}"}

    async def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update plugin configuration."""
        try:
            self.config.update(new_config)
            return {"status": "success", "message": "Configuration updated"}
        except Exception as e:
            return {"status": "error", "message": f"Config update failed: {e}"}

    async def _perform_chart_analysis(
        self, df: pd.DataFrame, config: ChartConfig
    ) -> StatisticalAnalysis:
        """Perform statistical analysis relevant to the chart."""
        summary_stats = self.data_processor.get_data_summary(df)

        analysis = StatisticalAnalysis(summary_stats=summary_stats)

        # Correlation analysis for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 2:
            analysis.correlation_matrix = (
                self.statistical_analyzer.correlation_analysis(df, numeric_cols)
            )

        # Distribution analysis for y-column
        if config.y_column in df.columns:
            analysis.distribution_analysis = (
                self.statistical_analyzer.distribution_analysis(df, config.y_column)
            )

        # Outlier analysis for numeric columns
        if pd.api.types.is_numeric_dtype(df[config.y_column]):
            analysis.outlier_analysis = self.statistical_analyzer.outlier_detection(
                df, config.y_column
            )

        # Trend analysis if both x and y are present
        if config.x_column in df.columns and config.y_column in df.columns:
            analysis.trend_analysis = self.statistical_analyzer.trend_analysis(
                df, config.x_column, config.y_column
            )

        return analysis

    def _generate_dashboard_html(self, charts: List[Dict[str, Any]]) -> str:
        """Generate HTML dashboard with multiple charts."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Data Visualization Dashboard</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }",
            ".dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }",
            ".chart-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
            ".chart-title { font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #333; }",
            ".chart-image { max-width: 100%; height: auto; }",
            ".stats { background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 12px; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>Data Visualization Dashboard</h1>",
            f"<p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
            "<div class='dashboard'>",
        ]

        for i, chart in enumerate(charts):
            chart_config = chart.get("chart_config", {})
            title = chart_config.get("title", f"Chart {i + 1}")

            html_parts.append("<div class='chart-container'>")
            html_parts.append(f"<div class='chart-title'>{title}</div>")

            if chart.get("html_content"):
                # Interactive chart
                html_parts.append(chart["html_content"])
            elif chart.get("image_data"):
                # Static chart
                html_parts.append(
                    f"<img class='chart-image' src='data:image/png;base64,{chart['image_data']}' alt='{title}'>"
                )

            # Add statistics if available
            if chart.get("statistical_analysis"):
                stats = chart["statistical_analysis"].get("summary_stats", {})
                if stats:
                    html_parts.append("<div class='stats'>")
                    html_parts.append(
                        f"<strong>Data Shape:</strong> {stats.get('shape', 'N/A')}<br>"
                    )
                    html_parts.append(
                        f"<strong>Columns:</strong> {len(stats.get('columns', []))}<br>"
                    )
                    html_parts.append("</div>")

            html_parts.append("</div>")

        html_parts.extend(["</div>", "</body>", "</html>"])

        return "\n".join(html_parts)


# Plugin entry point
def get_plugin():
    """Return the plugin instance."""
    return DataVisualizationPlugin()


# For testing
if __name__ == "__main__":

    async def test_plugin():
        plugin = DataVisualizationPlugin()
        await plugin.initialize()

        # Test with sample data
        sample_data = pd.DataFrame(
            {
                "x": range(10),
                "y": [x**2 + np.random.normal(0, 1) for x in range(10)],
                "category": ["A", "B"] * 5,
            }
        )

        # Test chart creation
        config = {
            "chart_type": "scatter",
            "title": "Test Scatter Plot",
            "x_column": "x",
            "y_column": "y",
            "color_column": "category",
        }

        result = await plugin.create_chart(
            sample_data.to_json(orient="records"), config
        )
        print("Chart creation result:", result["status"])

        await plugin.cleanup()

    import asyncio

    asyncio.run(test_plugin())
