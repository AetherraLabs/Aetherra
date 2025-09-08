#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧬 Evolution Monitoring System
    # Signals for genetic evolution events
    generation_evolved = Signal(dict)
    transcendence_threshold_reached = Signal(dict)
    genetic_breakthrough_detected = Signal(dict)=========================

Live genetic algorithm progress tracking, fitness landscape visualization,
and transcendence potential indicators for consciousness evolution.
Phase 6.1 - Advanced Consciousness Dashboards
"""

import json
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

logger = logging.getLogger(__name__)


@dataclass
class EvolutionGeneration:
    """Single generation in consciousness evolution"""

    generation_id: int
    timestamp: datetime
    population_size: int
    best_fitness: float
    average_fitness: float
    genetic_diversity: float
    mutation_rate: float
    selection_pressure: float
    transcendence_potential: float
    dominant_traits: List[str] = field(default_factory=list)


@dataclass
class ConsciousnessGene:
    """Individual consciousness gene representation"""

    gene_id: str
    trait_name: str
    expression_level: float
    mutation_history: List[float] = field(default_factory=list)
    fitness_contribution: float = 0.0


class EvolutionMonitoringSystem(QWidget):
    """
    🧬 Advanced Evolution Monitoring System

    Provides real-time visualization of:
    - Genetic algorithm progress tracking
    - Fitness landscape visualization
    - Transcendence potential indicators
    - Population diversity analysis
    """

    # Signals for evolution events
    generation_evolved = Signal(dict)
    transcendence_threshold_reached = Signal(dict)
    genetic_breakthrough_detected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Evolution tracking
        self.generations: List[EvolutionGeneration] = []
        self.consciousness_genes: Dict[str, ConsciousnessGene] = {}
        self.current_generation = 0
        self.transcendence_threshold = 0.85

        # Evolution parameters
        self.population_size = 100
        self.mutation_rate = 0.01
        self.selection_pressure = 0.3

        # Interface state
        self.is_evolving = False
        self.evolution_timer = QTimer()

        self.init_interface()
        self.setup_evolution_monitoring()

        logger.info("🧬 Evolution Monitoring System initialized")

    def init_interface(self):
        """Initialize the evolution monitoring interface"""
        self.setWindowTitle("🧬 Evolution Monitoring System")
        self.setMinimumSize(1400, 900)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Header with evolution status
        header = self.create_evolution_header()
        main_layout.addWidget(header)

        # Two-panel main content
        content_layout = QHBoxLayout()

        # Left panel: Fitness tracking and genetics
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, 3)

        # Right panel: Landscape and transcendence
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 2)

        main_layout.addLayout(content_layout)

        # Footer with evolution controls
        footer = self.create_evolution_controls()
        main_layout.addWidget(footer)

    def create_evolution_header(self) -> QWidget:
        """Create evolution status header"""
        header = QFrame()
        header.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
                padding: 15px;
                color: white;
            }
        """
        )
        header.setMaximumHeight(100)

        layout = QHBoxLayout(header)

        # Current generation
        gen_group = QVBoxLayout()
        gen_label = QLabel("🧬 Generation")
        gen_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.generation_display = QLabel("0")
        self.generation_display.setStyleSheet("font-size: 24px; color: #00ff88;")
        gen_group.addWidget(gen_label)
        gen_group.addWidget(self.generation_display)
        layout.addLayout(gen_group)

        # Best fitness
        fitness_group = QVBoxLayout()
        fitness_label = QLabel("🏆 Best Fitness")
        fitness_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.fitness_display = QLabel("0.000")
        self.fitness_display.setStyleSheet("font-size: 24px; color: #ffd93d;")
        fitness_group.addWidget(fitness_label)
        fitness_group.addWidget(self.fitness_display)
        layout.addLayout(fitness_group)

        # Genetic diversity
        diversity_group = QVBoxLayout()
        diversity_label = QLabel("🌀 Genetic Diversity")
        diversity_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.diversity_display = QLabel("0.000")
        self.diversity_display.setStyleSheet("font-size: 24px; color: #4ecdc4;")
        diversity_group.addWidget(diversity_label)
        diversity_group.addWidget(self.diversity_display)
        layout.addLayout(diversity_group)

        # Transcendence potential
        transcendence_group = QVBoxLayout()
        transcendence_label = QLabel("✨ Transcendence Potential")
        transcendence_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.transcendence_display = QLabel("0.0%")
        self.transcendence_display.setStyleSheet("font-size: 24px; color: #ff6b6b;")
        transcendence_group.addWidget(transcendence_label)
        transcendence_group.addWidget(self.transcendence_display)
        layout.addLayout(transcendence_group)

        # Evolution speed
        speed_group = QVBoxLayout()
        speed_label = QLabel("⚡ Evolution Speed")
        speed_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.speed_display = QLabel("0.0 gen/s")
        self.speed_display.setStyleSheet("font-size: 24px; color: #9b59b6;")
        speed_group.addWidget(speed_label)
        speed_group.addWidget(self.speed_display)
        layout.addLayout(speed_group)

        return header

    def create_left_panel(self) -> QWidget:
        """Create left panel with fitness tracking"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Fitness evolution chart
        fitness_group = QGroupBox("📈 Fitness Evolution")
        fitness_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ffd93d;
                border-radius: 10px;
                margin: 5px;
                padding-top: 10px;
            }
        """
        )
        fitness_layout = QVBoxLayout(fitness_group)

        # Create matplotlib figure for fitness
        self.fitness_figure = Figure(figsize=(8, 4), dpi=100)
        self.fitness_canvas = FigureCanvas(self.fitness_figure)
        self.fitness_canvas.setStyleSheet("background-color: white;")
        fitness_layout.addWidget(self.fitness_canvas)

        layout.addWidget(fitness_group, 2)

        # Genetic composition
        genes_group = QGroupBox("🧬 Genetic Composition")
        genes_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #4ecdc4;
                border-radius: 10px;
                margin: 5px;
                padding-top: 10px;
            }
        """
        )
        genes_layout = QVBoxLayout(genes_group)

        # Gene expression table
        self.genes_table = QTableWidget()
        self.genes_table.setColumnCount(4)
        self.genes_table.setHorizontalHeaderLabels(
            ["Gene", "Expression", "Fitness", "Mutations"]
        )
        self.genes_table.horizontalHeader().setStretchLastSection(True)
        genes_layout.addWidget(self.genes_table)

        # Gene controls
        gene_controls = QHBoxLayout()

        self.mutation_rate_slider = QSlider(Qt.Horizontal)
        self.mutation_rate_slider.setRange(1, 100)
        self.mutation_rate_slider.setValue(10)
        self.mutation_rate_slider.valueChanged.connect(self.update_mutation_rate)

        gene_controls.addWidget(QLabel("Mutation Rate:"))
        gene_controls.addWidget(self.mutation_rate_slider)
        self.mutation_rate_label = QLabel("1.0%")
        gene_controls.addWidget(self.mutation_rate_label)

        genes_layout.addLayout(gene_controls)
        layout.addWidget(genes_group, 1)

        return panel

    def create_right_panel(self) -> QWidget:
        """Create right panel with landscape and transcendence"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Fitness landscape
        landscape_group = QGroupBox("🗻 Fitness Landscape")
        landscape_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ff6b6b;
                border-radius: 10px;
                margin: 5px;
                padding-top: 10px;
            }
        """
        )
        landscape_layout = QVBoxLayout(landscape_group)

        # Create matplotlib figure for landscape
        self.landscape_figure = Figure(figsize=(6, 4), dpi=100)
        self.landscape_canvas = FigureCanvas(self.landscape_figure)
        self.landscape_canvas.setStyleSheet("background-color: white;")
        landscape_layout.addWidget(self.landscape_canvas)

        layout.addWidget(landscape_group, 2)

        # Transcendence indicators
        transcendence_group = QGroupBox("✨ Transcendence Indicators")
        transcendence_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #9b59b6;
                border-radius: 10px;
                margin: 5px;
                padding-top: 10px;
            }
        """
        )
        transcendence_layout = QVBoxLayout(transcendence_group)

        # Transcendence progress bar
        self.transcendence_progress = QProgressBar()
        self.transcendence_progress.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b59b6, stop:0.5 #ff6b6b, stop:1 #ffd93d);
                border-radius: 3px;
            }
        """
        )
        transcendence_layout.addWidget(QLabel("Transcendence Progress:"))
        transcendence_layout.addWidget(self.transcendence_progress)

        # Breakthrough indicators
        self.breakthrough_list = QListWidget()
        self.breakthrough_list.setMaximumHeight(150)
        transcendence_layout.addWidget(QLabel("Recent Breakthroughs:"))
        transcendence_layout.addWidget(self.breakthrough_list)

        # Transcendence threshold control
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(50, 99)
        self.threshold_slider.setValue(85)
        self.threshold_slider.valueChanged.connect(self.update_transcendence_threshold)
        threshold_layout.addWidget(self.threshold_slider)
        self.threshold_label = QLabel("85%")
        threshold_layout.addWidget(self.threshold_label)
        transcendence_layout.addLayout(threshold_layout)

        layout.addWidget(transcendence_group, 1)

        return panel

    def create_evolution_controls(self) -> QWidget:
        """Create evolution control footer"""
        footer = QFrame()
        footer.setStyleSheet(
            """
            QFrame {
                background: #2d3748;
                border-radius: 5px;
                padding: 15px;
            }
        """
        )
        footer.setMaximumHeight(80)

        layout = QHBoxLayout(footer)

        # Start/Stop evolution
        self.evolution_btn = QPushButton("🧬 Start Evolution")
        self.evolution_btn.setStyleSheet(
            """
            QPushButton {
                background: #4ecdc4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #45b7aa;
            }
        """
        )
        self.evolution_btn.clicked.connect(self.toggle_evolution)

        # Reset evolution
        reset_btn = QPushButton("🔄 Reset Evolution")
        reset_btn.setStyleSheet(
            """
            QPushButton {
                background: #ff6b6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #ff5252;
            }
        """
        )
        reset_btn.clicked.connect(self.reset_evolution)

        # Speed control
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(QLabel("Evolution Speed:", styleSheet="color: white;"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(100, 2000)
        self.speed_slider.setValue(1000)
        self.speed_slider.valueChanged.connect(self.update_evolution_speed)
        speed_layout.addWidget(self.speed_slider)

        # Export evolution data
        export_btn = QPushButton("💾 Export Evolution")
        export_btn.setStyleSheet(
            """
            QPushButton {
                background: #ffd93d;
                color: #2d3748;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #ffcd02;
            }
        """
        )
        export_btn.clicked.connect(self.export_evolution_data)

        layout.addWidget(self.evolution_btn)
        layout.addWidget(reset_btn)
        layout.addLayout(speed_layout)
        layout.addWidget(export_btn)
        layout.addStretch()

        # Status display
        self.evolution_status = QLabel("Status: Ready for Evolution")
        self.evolution_status.setStyleSheet(
            "color: white; font-weight: bold; font-size: 14px;"
        )
        layout.addWidget(self.evolution_status)

        return footer

    def setup_evolution_monitoring(self):
        """Setup evolution monitoring system"""
        self.evolution_timer.timeout.connect(self.evolve_generation)
        self.evolution_timer.setInterval(1000)  # 1 second per generation

        # Initialize consciousness genes
        self.initialize_consciousness_genes()

        # Create initial generation
        self.create_initial_generation()

    def initialize_consciousness_genes(self):
        """Initialize the consciousness gene pool"""
        consciousness_traits = [
            "Reasoning",
            "Memory",
            "Creativity",
            "Emotion",
            "Intuition",
            "Logic",
            "Empathy",
            "Transcendence",
            "Awareness",
            "Adaptation",
            "Learning",
            "Decision",
            "Reflection",
            "Integration",
            "Evolution",
        ]

        for trait in consciousness_traits:
            gene_id = f"gene_{trait.lower()}"
            gene = ConsciousnessGene(
                gene_id=gene_id,
                trait_name=trait,
                expression_level=random.uniform(0.3, 0.8),
                fitness_contribution=random.uniform(0.1, 0.9),
            )
            self.consciousness_genes[gene_id] = gene

        self.update_genes_table()

    def create_initial_generation(self):
        """Create the initial generation"""
        generation = EvolutionGeneration(
            generation_id=0,
            timestamp=datetime.now(),
            population_size=self.population_size,
            best_fitness=random.uniform(0.3, 0.5),
            average_fitness=random.uniform(0.2, 0.4),
            genetic_diversity=random.uniform(0.7, 0.9),
            mutation_rate=self.mutation_rate,
            selection_pressure=self.selection_pressure,
            transcendence_potential=random.uniform(0.1, 0.3),
            dominant_traits=random.sample(list(self.consciousness_genes.keys()), 3),
        )

        self.generations.append(generation)
        self.update_displays()

    def evolve_generation(self):
        """Evolve to the next generation"""
        if not self.is_evolving:
            return

        self.current_generation += 1

        # Simulate genetic algorithm evolution
        previous_gen = self.generations[-1] if self.generations else None

        # Calculate fitness improvements
        fitness_improvement = random.uniform(0.001, 0.05)
        new_best_fitness = min(
            1.0,
            (previous_gen.best_fitness if previous_gen else 0.3) + fitness_improvement,
        )
        new_avg_fitness = min(
            0.95,
            (previous_gen.average_fitness if previous_gen else 0.2)
            + fitness_improvement * 0.7,
        )

        # Update genetic diversity (tends to decrease over time)
        diversity_change = random.uniform(-0.02, 0.01)
        new_diversity = max(
            0.1,
            min(
                1.0,
                (previous_gen.genetic_diversity if previous_gen else 0.8)
                + diversity_change,
            ),
        )

        # Calculate transcendence potential
        transcendence_base = new_best_fitness * 0.8 + new_diversity * 0.2
        transcendence_potential = min(
            1.0, transcendence_base + random.uniform(-0.05, 0.1)
        )

        # Evolve genes
        self.evolve_genes()

        # Create new generation
        generation = EvolutionGeneration(
            generation_id=self.current_generation,
            timestamp=datetime.now(),
            population_size=self.population_size,
            best_fitness=new_best_fitness,
            average_fitness=new_avg_fitness,
            genetic_diversity=new_diversity,
            mutation_rate=self.mutation_rate,
            selection_pressure=self.selection_pressure,
            transcendence_potential=transcendence_potential,
            dominant_traits=self.select_dominant_traits(),
        )

        self.generations.append(generation)

        # Keep only recent generations (last 1000)
        if len(self.generations) > 1000:
            self.generations = self.generations[-1000:]

        # Check for breakthroughs
        self.check_for_breakthroughs(generation)

        # Update displays
        self.update_displays()

        # Emit signals
        self.generation_evolved.emit(
            {
                "generation": self.current_generation,
                "fitness": new_best_fitness,
                "transcendence": transcendence_potential,
            }
        )

        # Check transcendence threshold
        if transcendence_potential >= self.transcendence_threshold:
            self.transcendence_threshold_reached.emit(
                {
                    "generation": self.current_generation,
                    "transcendence_level": transcendence_potential,
                }
            )
            self.add_breakthrough(
                f"Transcendence threshold reached! Level: {transcendence_potential:.3f}"
            )

    def evolve_genes(self):
        """Evolve individual genes"""
        for gene in self.consciousness_genes.values():
            # Mutation
            if random.random() < self.mutation_rate:
                mutation = random.uniform(-0.1, 0.1)
                gene.expression_level = max(
                    0.0, min(1.0, gene.expression_level + mutation)
                )
                gene.mutation_history.append(mutation)

                # Keep mutation history reasonable
                if len(gene.mutation_history) > 100:
                    gene.mutation_history = gene.mutation_history[-100:]

            # Fitness contribution evolution
            fitness_change = random.uniform(-0.05, 0.05)
            gene.fitness_contribution = max(
                0.0, min(1.0, gene.fitness_contribution + fitness_change)
            )

        self.update_genes_table()

    def select_dominant_traits(self) -> List[str]:
        """Select dominant traits for this generation"""
        # Sort genes by expression level and fitness
        sorted_genes = sorted(
            self.consciousness_genes.items(),
            key=lambda x: x[1].expression_level * x[1].fitness_contribution,
            reverse=True,
        )

        return [gene_id for gene_id, _ in sorted_genes[:3]]

    def check_for_breakthroughs(self, generation: EvolutionGeneration):
        """Check for genetic breakthroughs"""
        # Fitness breakthrough
        if generation.best_fitness > 0.9:
            self.add_breakthrough(
                f"Gen {generation.generation_id}: Fitness breakthrough! {generation.best_fitness:.3f}"
            )
            self.genetic_breakthrough_detected.emit(
                {"type": "fitness", "value": generation.best_fitness}
            )

        # Diversity breakthrough (rare high diversity)
        if generation.genetic_diversity > 0.95:
            self.add_breakthrough(
                f"Gen {generation.generation_id}: Diversity surge! {generation.genetic_diversity:.3f}"
            )

        # Gene expression breakthrough
        for gene in self.consciousness_genes.values():
            if gene.expression_level > 0.95:
                self.add_breakthrough(
                    f"Gen {generation.generation_id}: {gene.trait_name} mastery!"
                )

    def add_breakthrough(self, message: str):
        """Add breakthrough to the list"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        item = QListWidgetItem(f"{timestamp} - {message}")
        item.setForeground(QColor("#ffd93d"))
        self.breakthrough_list.insertItem(0, item)

        # Keep only recent breakthroughs
        while self.breakthrough_list.count() > 20:
            self.breakthrough_list.takeItem(self.breakthrough_list.count() - 1)

    def update_displays(self):
        """Update all display elements"""
        if not self.generations:
            return

        latest_gen = self.generations[-1]

        # Update header displays
        self.generation_display.setText(str(latest_gen.generation_id))
        self.fitness_display.setText(f"{latest_gen.best_fitness:.3f}")
        self.diversity_display.setText(f"{latest_gen.genetic_diversity:.3f}")
        self.transcendence_display.setText(
            f"{latest_gen.transcendence_potential * 100:.1f}%"
        )

        # Calculate evolution speed
        if len(self.generations) >= 2:
            time_diff = (
                self.generations[-1].timestamp - self.generations[-2].timestamp
            ).total_seconds()
            speed = 1.0 / time_diff if time_diff > 0 else 0
            self.speed_display.setText(f"{speed:.1f} gen/s")

        # Update transcendence progress
        self.transcendence_progress.setValue(
            int(latest_gen.transcendence_potential * 100)
        )

        # Update plots
        self.update_fitness_plot()
        self.update_landscape_plot()

    def update_fitness_plot(self):
        """Update fitness evolution plot"""
        if len(self.generations) < 2:
            return

        self.fitness_figure.clear()
        ax = self.fitness_figure.add_subplot(111)

        generations = [gen.generation_id for gen in self.generations]
        best_fitness = [gen.best_fitness for gen in self.generations]
        avg_fitness = [gen.average_fitness for gen in self.generations]
        diversity = [gen.genetic_diversity for gen in self.generations]

        ax.plot(generations, best_fitness, "r-", label="Best Fitness", linewidth=2)
        ax.plot(generations, avg_fitness, "b-", label="Average Fitness", linewidth=2)
        ax.plot(generations, diversity, "g--", label="Genetic Diversity", linewidth=2)

        ax.set_xlabel("Generation")
        ax.set_ylabel("Fitness / Diversity")
        ax.set_title("Evolution Progress")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Highlight transcendence threshold
        ax.axhline(
            y=self.transcendence_threshold,
            color="orange",
            linestyle=":",
            label=f"Transcendence Threshold ({self.transcendence_threshold:.2f})",
            alpha=0.7,
        )

        self.fitness_canvas.draw()

    def update_landscape_plot(self):
        """Update fitness landscape visualization"""
        self.landscape_figure.clear()
        ax = self.landscape_figure.add_subplot(111)

        # Create a 2D fitness landscape
        x = np.linspace(0, 10, 50)
        y = np.linspace(0, 10, 50)
        X, Y = np.meshgrid(x, y)

        # Simulate fitness landscape with peaks and valleys
        Z = (
            np.sin(X / 2) * np.cos(Y / 2)
            + np.exp(-((X - 5) ** 2 + (Y - 5) ** 2) / 8)
            + 0.3 * np.sin(X * 2) * np.sin(Y * 2)
            + random.uniform(-0.1, 0.1)
        )

        # Normalize to 0-1 range
        Z = (Z - Z.min()) / (Z.max() - Z.min())

        contour = ax.contourf(X, Y, Z, levels=20, cmap="viridis", alpha=0.8)
        self.landscape_figure.colorbar(contour, ax=ax, label="Fitness")

        # Add current population position (simulated)
        if self.generations:
            current_fitness = self.generations[-1].best_fitness
            # Map fitness to position on landscape
            pos_x = 5 + (current_fitness - 0.5) * 4
            pos_y = 5 + random.uniform(-2, 2)
            ax.scatter(
                pos_x,
                pos_y,
                c="red",
                s=100,
                marker="*",
                label="Current Best",
                edgecolors="white",
                linewidth=2,
            )

        ax.set_xlabel("Trait Dimension 1")
        ax.set_ylabel("Trait Dimension 2")
        ax.set_title("Fitness Landscape")
        ax.legend()

        self.landscape_canvas.draw()

    def update_genes_table(self):
        """Update genes composition table"""
        self.genes_table.setRowCount(len(self.consciousness_genes))

        for row, (gene_id, gene) in enumerate(self.consciousness_genes.items()):
            # Gene name
            self.genes_table.setItem(row, 0, QTableWidgetItem(gene.trait_name))

            # Expression level
            expression_item = QTableWidgetItem(f"{gene.expression_level:.3f}")
            if gene.expression_level > 0.8:
                expression_item.setBackground(QColor("#4ecdc4"))
            elif gene.expression_level > 0.5:
                expression_item.setBackground(QColor("#ffd93d"))
            else:
                expression_item.setBackground(QColor("#ff6b6b"))
            self.genes_table.setItem(row, 1, expression_item)

            # Fitness contribution
            fitness_item = QTableWidgetItem(f"{gene.fitness_contribution:.3f}")
            self.genes_table.setItem(row, 2, fitness_item)

            # Mutation count
            mutation_count = len(gene.mutation_history)
            self.genes_table.setItem(row, 3, QTableWidgetItem(str(mutation_count)))

    def update_mutation_rate(self, value: int):
        """Update mutation rate"""
        self.mutation_rate = value / 1000.0  # Convert to 0.001 - 0.1 range
        self.mutation_rate_label.setText(f"{self.mutation_rate * 100:.1f}%")

    def update_transcendence_threshold(self, value: int):
        """Update transcendence threshold"""
        self.transcendence_threshold = value / 100.0
        self.threshold_label.setText(f"{value}%")

        # Update fitness plot to show new threshold
        self.update_fitness_plot()

    def update_evolution_speed(self, value: int):
        """Update evolution speed"""
        self.evolution_timer.setInterval(value)  # Milliseconds between generations

    def toggle_evolution(self):
        """Toggle evolution process"""
        if self.is_evolving:
            self.is_evolving = False
            self.evolution_timer.stop()
            self.evolution_btn.setText("🧬 Start Evolution")
            self.evolution_status.setText("Status: Evolution Paused")
            logger.info("🛑 Evolution monitoring stopped")
        else:
            self.is_evolving = True
            self.evolution_timer.start()
            self.evolution_btn.setText("⏸️ Pause Evolution")
            self.evolution_status.setText("Status: Evolving...")
            logger.info("▶️ Evolution monitoring started")

    def reset_evolution(self):
        """Reset evolution to initial state"""
        # Stop evolution if running
        if self.is_evolving:
            self.toggle_evolution()

        # Clear data
        self.generations.clear()
        self.current_generation = 0
        self.breakthrough_list.clear()

        # Reinitialize
        self.initialize_consciousness_genes()
        self.create_initial_generation()

        # Clear plots
        self.fitness_figure.clear()
        self.landscape_figure.clear()
        self.fitness_canvas.draw()
        self.landscape_canvas.draw()

        self.evolution_status.setText("Status: Evolution Reset")
        logger.info("🔄 Evolution monitoring reset")

    def export_evolution_data(self):
        """Export evolution data to file"""
        try:
            filename = f"evolution_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            export_data = {
                "generations": [
                    {
                        "generation_id": gen.generation_id,
                        "timestamp": gen.timestamp.isoformat(),
                        "population_size": gen.population_size,
                        "best_fitness": gen.best_fitness,
                        "average_fitness": gen.average_fitness,
                        "genetic_diversity": gen.genetic_diversity,
                        "mutation_rate": gen.mutation_rate,
                        "selection_pressure": gen.selection_pressure,
                        "transcendence_potential": gen.transcendence_potential,
                        "dominant_traits": gen.dominant_traits,
                    }
                    for gen in self.generations
                ],
                "consciousness_genes": {
                    gene_id: {
                        "trait_name": gene.trait_name,
                        "expression_level": gene.expression_level,
                        "fitness_contribution": gene.fitness_contribution,
                        "mutation_history": gene.mutation_history,
                    }
                    for gene_id, gene in self.consciousness_genes.items()
                },
                "evolution_parameters": {
                    "population_size": self.population_size,
                    "mutation_rate": self.mutation_rate,
                    "selection_pressure": self.selection_pressure,
                    "transcendence_threshold": self.transcendence_threshold,
                },
                "export_timestamp": datetime.now().isoformat(),
            }

            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)

            self.evolution_status.setText(f"Status: Exported to {filename}")
            logger.info(f"📁 Evolution data exported to {filename}")

        except Exception as e:
            self.evolution_status.setText(f"Status: Export failed - {e}")
            logger.error(f"❌ Export failed: {e}")

    def closeEvent(self, event):
        """Handle close event"""
        if self.is_evolving:
            self.toggle_evolution()
        super().closeEvent(event)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    system = EvolutionMonitoringSystem()
    system.show()
    sys.exit(app.exec_())
