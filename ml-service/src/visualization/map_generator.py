# src/visualization/map_generator.py
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
import io
import base64
import json
import logging
from typing import Optional, Tuple, Dict, Any, Union
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class HeatmapConfig:
    """Configuration for heatmap generation"""
    figsize: Tuple[float, float] = (10, 8)
    dpi: int = 150
    cmap: str = 'viridis'
    interpolation: str = 'nearest'
    show_colorbar: bool = True
    show_grid: bool = False
    title: Optional[str] = None
    xlabel: str = 'X Position (mm)'
    ylabel: str = 'Y Position (mm)'
    colorbar_label: str = 'Purity (%)'
    vmin: Optional[float] = None
    vmax: Optional[float] = None
    mask_nan: bool = True
    nan_color: str = 'gray'

class MapGenerator:
    """
    Generates heatmaps and visualizations from 2D purity scan data
    """
    
    def __init__(self, config: Optional[HeatmapConfig] = None):
        self.config = config or HeatmapConfig()
    
    def generate_heatmap(self, 
                        purity_grid: np.ndarray,
                        x_positions: Optional[np.ndarray] = None,
                        y_positions: Optional[np.ndarray] = None,
                        output_path: Optional[str] = None,
                        return_bytes: bool = True,
                        config_override: Optional[HeatmapConfig] = None) -> Optional[bytes]:
        """
        Generate heatmap from purity grid
        
        Args:
            purity_grid: 2D numpy array of purity values (ny, nx)
            x_positions: X coordinate values (optional)
            y_positions: Y coordinate values (optional)
            output_path: Path to save PNG file (optional)
            return_bytes: Whether to return image as bytes
            config_override: Override default configuration
            
        Returns:
            PNG image as bytes if return_bytes=True
        """
        config = config_override or self.config
        
        try:
            # Create figure and axis
            fig, ax = plt.subplots(figsize=config.figsize, dpi=config.dpi)
            
            # Handle NaN values
            plot_grid = purity_grid.copy()
            if config.mask_nan:
                plot_grid = np.ma.masked_invalid(plot_grid)
            
            # Set up extent for proper coordinate mapping
            if x_positions is not None and y_positions is not None:
                extent = [x_positions[0], x_positions[-1], y_positions[0], y_positions[-1]]
            else:
                extent = [0, purity_grid.shape[1], 0, purity_grid.shape[0]]
            
            # Create heatmap
            im = ax.imshow(plot_grid, 
                          origin='lower',
                          aspect='auto',
                          interpolation=config.interpolation,
                          cmap=config.cmap,
                          vmin=config.vmin,
                          vmax=config.vmax,
                          extent=extent)
            
            # Set NaN color if needed
            if config.mask_nan:
                im.set_bad(color=config.nan_color, alpha=0.5)
            
            # Add colorbar
            if config.show_colorbar:
                cbar = plt.colorbar(im, ax=ax, label=config.colorbar_label)
                cbar.ax.tick_params(labelsize=10)
            
            # Customize plot
            ax.set_xlabel(config.xlabel, fontsize=12)
            ax.set_ylabel(config.ylabel, fontsize=12)
            
            if config.title:
                ax.set_title(config.title, fontsize=14, fontweight='bold')
            
            if config.show_grid:
                ax.grid(True, alpha=0.3)
            
            # Tight layout
            plt.tight_layout()
            
            # Save and/or return bytes
            result_bytes = None
            
            if return_bytes or output_path:
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=config.dpi, bbox_inches='tight')
                buf.seek(0)
                result_bytes = buf.read()
                buf.close()
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(result_bytes)
                logger.info(f"Heatmap saved to {output_path}")
            
            plt.close(fig)
            
            return result_bytes if return_bytes else None
            
        except Exception as e:
            logger.error(f"Error generating heatmap: {e}")
            plt.close('all')  # Clean up any open figures
            raise
    
    def generate_contour_map(self,
                           purity_grid: np.ndarray,
                           x_positions: Optional[np.ndarray] = None,
                           y_positions: Optional[np.ndarray] = None,
                           levels: Optional[Union[int, list]] = None,
                           output_path: Optional[str] = None,
                           return_bytes: bool = True) -> Optional[bytes]:
        """
        Generate contour map from purity grid
        
        Args:
            purity_grid: 2D numpy array of purity values
            x_positions: X coordinate values
            y_positions: Y coordinate values
            levels: Contour levels (int for number of levels, list for specific values)
            output_path: Path to save PNG file
            return_bytes: Whether to return image as bytes
            
        Returns:
            PNG image as bytes if return_bytes=True
        """
        try:
            fig, ax = plt.subplots(figsize=self.config.figsize, dpi=self.config.dpi)
            
            # Set up coordinate grids
            if x_positions is not None and y_positions is not None:
                X, Y = np.meshgrid(x_positions, y_positions)
            else:
                X, Y = np.meshgrid(range(purity_grid.shape[1]), range(purity_grid.shape[0]))
            
            # Create contour plot
            if levels is None:
                levels = 10
            
            # Filled contours
            cs_filled = ax.contourf(X, Y, purity_grid, levels=levels, cmap=self.config.cmap)
            
            # Contour lines
            cs_lines = ax.contour(X, Y, purity_grid, levels=levels, colors='black', alpha=0.4, linewidths=0.5)
            
            # Add labels to contour lines
            ax.clabel(cs_lines, inline=True, fontsize=8, fmt='%.1f')
            
            # Colorbar
            if self.config.show_colorbar:
                cbar = plt.colorbar(cs_filled, ax=ax, label=self.config.colorbar_label)
                cbar.ax.tick_params(labelsize=10)
            
            # Customize plot
            ax.set_xlabel(self.config.xlabel, fontsize=12)
            ax.set_ylabel(self.config.ylabel, fontsize=12)
            
            if self.config.title:
                ax.set_title(f"{self.config.title} (Contour)", fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            # Save and/or return bytes
            result_bytes = None
            
            if return_bytes or output_path:
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=self.config.dpi, bbox_inches='tight')
                buf.seek(0)
                result_bytes = buf.read()
                buf.close()
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(result_bytes)
                logger.info(f"Contour map saved to {output_path}")
            
            plt.close(fig)
            
            return result_bytes if return_bytes else None
            
        except Exception as e:
            logger.error(f"Error generating contour map: {e}")
            plt.close('all')
            raise
    
    def generate_3d_surface(self,
                          purity_grid: np.ndarray,
                          x_positions: Optional[np.ndarray] = None,
                          y_positions: Optional[np.ndarray] = None,
                          output_path: Optional[str] = None,
                          return_bytes: bool = True) -> Optional[bytes]:
        """
        Generate 3D surface plot from purity grid
        
        Args:
            purity_grid: 2D numpy array of purity values
            x_positions: X coordinate values
            y_positions: Y coordinate values
            output_path: Path to save PNG file
            return_bytes: Whether to return image as bytes
            
        Returns:
            PNG image as bytes if return_bytes=True
        """
        try:
            from mpl_toolkits.mplot3d import Axes3D
            
            fig = plt.figure(figsize=self.config.figsize, dpi=self.config.dpi)
            ax = fig.add_subplot(111, projection='3d')
            
            # Set up coordinate grids
            if x_positions is not None and y_positions is not None:
                X, Y = np.meshgrid(x_positions, y_positions)
            else:
                X, Y = np.meshgrid(range(purity_grid.shape[1]), range(purity_grid.shape[0]))
            
            # Create surface plot
            surf = ax.plot_surface(X, Y, purity_grid, 
                                 cmap=self.config.cmap,
                                 alpha=0.9,
                                 linewidth=0,
                                 antialiased=True)
            
            # Customize plot
            ax.set_xlabel(self.config.xlabel, fontsize=12)
            ax.set_ylabel(self.config.ylabel, fontsize=12)
            ax.set_zlabel(self.config.colorbar_label, fontsize=12)
            
            if self.config.title:
                ax.set_title(f"{self.config.title} (3D Surface)", fontsize=14, fontweight='bold')
            
            # Add colorbar
            if self.config.show_colorbar:
                fig.colorbar(surf, ax=ax, label=self.config.colorbar_label, shrink=0.5)
            
            plt.tight_layout()
            
            # Save and/or return bytes
            result_bytes = None
            
            if return_bytes or output_path:
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=self.config.dpi, bbox_inches='tight')
                buf.seek(0)
                result_bytes = buf.read()
                buf.close()
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(result_bytes)
                logger.info(f"3D surface plot saved to {output_path}")
            
            plt.close(fig)
            
            return result_bytes if return_bytes else None
            
        except ImportError:
            logger.warning("3D plotting not available - missing mplot3d")
            return self.generate_heatmap(purity_grid, x_positions, y_positions, output_path, return_bytes)
        except Exception as e:
            logger.error(f"Error generating 3D surface: {e}")
            plt.close('all')
            raise
    
    def generate_statistics_overlay(self,
                                  purity_grid: np.ndarray,
                                  x_positions: Optional[np.ndarray] = None,
                                  y_positions: Optional[np.ndarray] = None,
                                  output_path: Optional[str] = None,
                                  return_bytes: bool = True) -> Optional[bytes]:
        """
        Generate heatmap with statistics overlay
        
        Args:
            purity_grid: 2D numpy array of purity values
            x_positions: X coordinate values
            y_positions: Y coordinate values
            output_path: Path to save PNG file
            return_bytes: Whether to return image as bytes
            
        Returns:
            PNG image as bytes if return_bytes=True
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=self.config.dpi)
            
            # Main heatmap
            if x_positions is not None and y_positions is not None:
                extent = [x_positions[0], x_positions[-1], y_positions[0], y_positions[-1]]
            else:
                extent = [0, purity_grid.shape[1], 0, purity_grid.shape[0]]
            
            im = ax1.imshow(purity_grid, 
                           origin='lower',
                           aspect='auto',
                           interpolation=self.config.interpolation,
                           cmap=self.config.cmap,
                           extent=extent)
            
            ax1.set_xlabel(self.config.xlabel)
            ax1.set_ylabel(self.config.ylabel)
            ax1.set_title('Purity Map')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax1, label=self.config.colorbar_label)
            
            # Statistics panel
            valid_data = purity_grid[~np.isnan(purity_grid)]
            
            if len(valid_data) > 0:
                stats = {
                    'Mean': np.mean(valid_data),
                    'Median': np.median(valid_data),
                    'Std Dev': np.std(valid_data),
                    'Min': np.min(valid_data),
                    'Max': np.max(valid_data),
                    'Range': np.max(valid_data) - np.min(valid_data),
                    'Valid Points': len(valid_data),
                    'Total Points': purity_grid.size
                }
                
                # Histogram
                ax2.hist(valid_data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
                ax2.axvline(stats['Mean'], color='red', linestyle='--', label=f"Mean: {stats['Mean']:.1f}")
                ax2.axvline(stats['Median'], color='orange', linestyle='--', label=f"Median: {stats['Median']:.1f}")
                
                ax2.set_xlabel('Purity (%)')
                ax2.set_ylabel('Frequency')
                ax2.set_title('Purity Distribution')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                
                # Add statistics text
                stats_text = '\n'.join([f'{k}: {v:.2f}' if isinstance(v, float) else f'{k}: {v}' 
                                      for k, v in stats.items()])
                ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, 
                        verticalalignment='top', fontfamily='monospace',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            else:
                ax2.text(0.5, 0.5, 'No valid data', transform=ax2.transAxes,
                        ha='center', va='center', fontsize=16)
            
            plt.tight_layout()
            
            # Save and/or return bytes
            result_bytes = None
            
            if return_bytes or output_path:
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=self.config.dpi, bbox_inches='tight')
                buf.seek(0)
                result_bytes = buf.read()
                buf.close()
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(result_bytes)
                logger.info(f"Statistics overlay saved to {output_path}")
            
            plt.close(fig)
            
            return result_bytes if return_bytes else None
            
        except Exception as e:
            logger.error(f"Error generating statistics overlay: {e}")
            plt.close('all')
            raise
    
    def export_data(self,
                   purity_grid: np.ndarray,
                   x_positions: Optional[np.ndarray] = None,
                   y_positions: Optional[np.ndarray] = None,
                   output_path: str = "scan_data",
                   formats: list = ["json", "csv"]) -> Dict[str, str]:
        """
        Export scan data in multiple formats
        
        Args:
            purity_grid: 2D numpy array of purity values
            x_positions: X coordinate values
            y_positions: Y coordinate values
            output_path: Base path for output files (without extension)
            formats: List of formats to export ("json", "csv", "npz")
            
        Returns:
            Dictionary mapping format to output file path
        """
        output_files = {}
        
        try:
            # Prepare data
            if x_positions is None:
                x_positions = np.arange(purity_grid.shape[1])
            if y_positions is None:
                y_positions = np.arange(purity_grid.shape[0])
            
            for fmt in formats:
                if fmt.lower() == "json":
                    # JSON export
                    json_path = f"{output_path}.json"
                    data = {
                        "grid": purity_grid.tolist(),
                        "x_positions": x_positions.tolist(),
                        "y_positions": y_positions.tolist(),
                        "shape": purity_grid.shape,
                        "statistics": {
                            "mean": float(np.nanmean(purity_grid)),
                            "std": float(np.nanstd(purity_grid)),
                            "min": float(np.nanmin(purity_grid)),
                            "max": float(np.nanmax(purity_grid)),
                            "valid_points": int(np.sum(~np.isnan(purity_grid)))
                        }
                    }
                    
                    with open(json_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    output_files["json"] = json_path
                
                elif fmt.lower() == "csv":
                    # CSV export (flattened data)
                    csv_path = f"{output_path}.csv"
                    
                    # Create flattened data
                    rows = []
                    for i, y in enumerate(y_positions):
                        for j, x in enumerate(x_positions):
                            purity = purity_grid[i, j]
                            rows.append({
                                "x_mm": x,
                                "y_mm": y,
                                "purity_percent": purity,
                                "row_index": i,
                                "col_index": j
                            })
                    
                    # Write CSV
                    import csv
                    with open(csv_path, 'w', newline='') as f:
                        if rows:
                            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                            writer.writeheader()
                            writer.writerows(rows)
                    output_files["csv"] = csv_path
                
                elif fmt.lower() == "npz":
                    # NumPy compressed format
                    npz_path = f"{output_path}.npz"
                    np.savez_compressed(npz_path,
                                      purity_grid=purity_grid,
                                      x_positions=x_positions,
                                      y_positions=y_positions)
                    output_files["npz"] = npz_path
            
            logger.info(f"Data exported to {len(output_files)} formats")
            return output_files
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            raise
    
    def create_animated_scan(self,
                           scan_history: list,
                           output_path: str,
                           fps: int = 5) -> str:
        """
        Create animated GIF showing scan progress
        
        Args:
            scan_history: List of partial purity grids showing scan progress
            output_path: Path for output GIF file
            fps: Frames per second
            
        Returns:
            Path to created GIF file
        """
        try:
            from matplotlib.animation import PillowWriter
            
            fig, ax = plt.subplots(figsize=self.config.figsize, dpi=100)
            
            # Set up the plot
            if scan_history:
                vmin = np.nanmin([np.nanmin(grid) for grid in scan_history if grid.size > 0])
                vmax = np.nanmax([np.nanmax(grid) for grid in scan_history if grid.size > 0])
            else:
                vmin, vmax = 0, 100
            
            writer = PillowWriter(fps=fps)
            
            with writer.saving(fig, output_path, dpi=100):
                for i, grid in enumerate(scan_history):
                    ax.clear()
                    
                    if grid.size > 0:
                        im = ax.imshow(grid, origin='lower', aspect='auto',
                                     cmap=self.config.cmap, vmin=vmin, vmax=vmax)
                        ax.set_title(f'Scan Progress: Frame {i+1}/{len(scan_history)}')
                        ax.set_xlabel(self.config.xlabel)
                        ax.set_ylabel(self.config.ylabel)
                    
                    writer.grab_frame()
            
            plt.close(fig)
            logger.info(f"Animated scan saved to {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("Animation not available - missing Pillow")
            raise
        except Exception as e:
            logger.error(f"Error creating animated scan: {e}")
            plt.close('all')
            raise


# Convenience functions
def generate_heatmap(purity_grid: np.ndarray,
                    x_positions: Optional[np.ndarray] = None,
                    y_positions: Optional[np.ndarray] = None,
                    output_path: Optional[str] = None,
                    **kwargs) -> bytes:
    """
    Convenience function to generate a heatmap
    
    Args:
        purity_grid: 2D numpy array of purity values
        x_positions: X coordinate values
        y_positions: Y coordinate values
        output_path: Path to save PNG file
        **kwargs: Additional configuration options
        
    Returns:
        PNG image as bytes
    """
    generator = MapGenerator()
    return generator.generate_heatmap(purity_grid, x_positions, y_positions, output_path, **kwargs)

def export_scan_data(purity_grid: np.ndarray,
                    x_positions: Optional[np.ndarray] = None,
                    y_positions: Optional[np.ndarray] = None,
                    output_path: str = "scan_data") -> Dict[str, str]:
    """
    Convenience function to export scan data
    
    Args:
        purity_grid: 2D numpy array of purity values
        x_positions: X coordinate values
        y_positions: Y coordinate values
        output_path: Base path for output files
        
    Returns:
        Dictionary mapping format to file path
    """
    generator = MapGenerator()
    return generator.export_data(purity_grid, x_positions, y_positions, output_path)
