# ================================================================
#  CANCER CELL SIMULATOR  (Year 9 Science Fair Investigation)
# ================================================================
#
#  IMPORTANT DISCLAIMER:
#  This is an educational model only. It is NOT medically accurate
#  and must not be used for real medical decisions.
#
#  AIM:
#  To investigate how cancer growth and treatment resistance affect
#  the success of chemotherapy and radiation in a simple simulation.
#
#  HOW TO RUN:
#      python cancer_simulation.py
#
#  HOW TO USE THE WINDOW:
#      START / PAUSE = start or stop the experiment
#      CHEMO         = apply chemotherapy once
#      RADIATION     = apply radiation once
#
#  CELL COLOURS:
#      green  = healthy cells
#      orange = mutated cells
#      red    = cancer cells
#      purple = treatment-resistant cancer cells
#
#  WHAT TO WATCH:
#      Resistant cancer cells are harder to kill. If purple cells become
#      common, the cancer becomes harder to control.
# ================================================================


import random
import sys

# numpy stores the 50 x 50 grid of cell numbers.
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# matplotlib draws the grid, buttons, legend, and final graph.
try:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    from matplotlib.widgets import Button
    HAS_GRAPHICS = True
except ImportError:
    HAS_GRAPHICS = False


# ================================================================
#  SETTINGS -- CHANGE THESE FOR YOUR SCIENCE FAIR EXPERIMENT
# ================================================================

grid_size = 50          # the grid is 50 squares wide and 50 squares tall
generations = 120       # how many time steps the experiment runs for
animation_speed = 350   # milliseconds between generations; bigger = slower

# Starting cells.
start_healthy_fraction = 0.35   # how much of the grid starts healthy
start_cancer_cells = 7          # starting cancer cells, placed in a cluster

# Cell growth chances each generation.
healthy_division_chance = 0.08
mutated_division_chance = 0.10
cancer_division_chance = 0.42
resistant_division_chance = 0.36

# Mutation and resistance chances.
mutation_chance = 0.006          # healthy cell -> mutated cell
mutated_to_cancer_chance = 0.025 # mutated cell -> cancer cell
pre_existing_resistance_chance = 0.10  # cancer can start with rare resistance
spontaneous_resistance_chance = 0.004  # cancer division can make resistance
resistance_chance = 0.10         # surviving cancer -> resistant after treatment

# Crowded cancer cells sometimes die from poor local conditions.
crowded_cancer_death_chance = 0.015
crowded_resistant_death_chance = 0.010

# Treatment strength.
# Treatments reduce cancer strongly, but also harm some healthy cells.
# Resistant cancer cells are harder to kill, not impossible to kill.
chemo_cancer_kill_rate = 0.70
chemo_resistant_kill_rate = 0.22
chemo_healthy_kill_rate = 0.12
radiation_cancer_kill_rate = 0.55
radiation_resistant_kill_rate = 0.15
radiation_healthy_kill_rate = 0.06

# Fast mode has no buttons, so it uses these automatic treatment generations.
fast_mode_chemo_generations = [40, 60, 80, 100]
fast_mode_radiation_generations = [50, 70, 90, 110]


# ================================================================
#  CELL TYPES
# ================================================================

EMPTY = 0       # no cell
HEALTHY = 1     # normal cell
MUTATED = 2     # damaged cell
CANCER = 3      # cancer cell
RESISTANT = 4   # cancer cell that is harder to kill

cell_colours = [
    "#111111",  # empty space
    "#2ecc40",  # healthy = green
    "#ff851b",  # mutated = orange
    "#ff4136",  # cancer = red
    "#b10dc9",  # resistant = purple
]

cell_colour_map = None
if HAS_GRAPHICS:
    cell_colour_map = ListedColormap(cell_colours)


# ================================================================
#  SCIENCE MODEL
# ================================================================

def make_starting_grid():
    """Create generation 0 with healthy cells and a small cancer cluster."""
    grid = np.zeros((grid_size, grid_size), dtype=int)

    # Scatter healthy cells around the grid.
    for row in range(grid_size):
        for col in range(grid_size):
            if random.random() < start_healthy_fraction:
                grid[row][col] = HEALTHY

    # Put the starting cancer cells close together.
    # This makes cancer grow as a tumour-like cluster, not random dots.
    middle = grid_size // 2
    placed = 0
    while placed < start_cancer_cells:
        row = middle + random.randint(-2, 2)
        col = middle + random.randint(-2, 2)
        if 0 <= row < grid_size and 0 <= col < grid_size:
            if random.random() < pre_existing_resistance_chance:
                grid[row][col] = RESISTANT
            else:
                grid[row][col] = CANCER
            placed += 1

    return grid


def random_empty_neighbour(grid, row, col):
    "Return one empty neighbouring square, or None if there is no space."
    neighbours = [
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]

    empty_spots = []
    for next_row, next_col in neighbours:
        inside_grid = (
            0 <= next_row < grid_size and
            0 <= next_col < grid_size
        )
        if inside_grid and grid[next_row][next_col] == EMPTY:
            empty_spots.append((next_row, next_col))

    if empty_spots:
        return random.choice(empty_spots)
    return None


def apply_growth(grid):
    "Run one generation of growth, mutation, and cancer spread."
    all_positions = [
        (row, col)
        for row in range(grid_size)
        for col in range(grid_size)
    ]
    random.shuffle(all_positions)

    for row, col in all_positions:
        cell = grid[row][col]

        if cell == HEALTHY:
            # Healthy cells can randomly become mutated by DNA damage.
            if random.random() < mutation_chance:
                grid[row][col] = MUTATED
                continue

            # Healthy cells divide slowly.
            if random.random() < healthy_division_chance:
                spot = random_empty_neighbour(grid, row, col)
                if spot:
                    grid[spot[0]][spot[1]] = HEALTHY

        elif cell == MUTATED:
            # Mutated cells can become cancer cells.
            if random.random() < mutated_to_cancer_chance:
                grid[row][col] = CANCER
                continue

            # Mutated cells divide a little faster than healthy cells.
            if random.random() < mutated_division_chance:
                spot = random_empty_neighbour(grid, row, col)
                if spot:
                    grid[spot[0]][spot[1]] = MUTATED

        elif cell == CANCER:
            # Cancer cells divide quickly into nearby empty spaces.
            spot = random_empty_neighbour(grid, row, col)
            if spot and random.random() < cancer_division_chance:
                if random.random() < spontaneous_resistance_chance:
                    grid[spot[0]][spot[1]] = RESISTANT
                else:
                    grid[spot[0]][spot[1]] = CANCER
            elif spot is None and random.random() < crowded_cancer_death_chance:
                grid[row][col] = EMPTY

        elif cell == RESISTANT:
            # Resistant cells divide too, but crowding can still kill them.
            spot = random_empty_neighbour(grid, row, col)
            if spot and random.random() < resistant_division_chance:
                grid[spot[0]][spot[1]] = RESISTANT
            elif spot is None and random.random() < crowded_resistant_death_chance:
                grid[row][col] = EMPTY


def apply_treatment(grid, cancer_kill_rate, resistant_kill_rate,
                    healthy_kill_rate):
    """Apply chemotherapy or radiation once.

    Treatment kills many red cancer cells and some green healthy cells.
    Some red cancer cells survive and become purple resistant cells.
    Purple resistant cells are harder to kill, but treatment can still kill some.
    """
    for row in range(grid_size):
        for col in range(grid_size):
            cell = grid[row][col]

            if cell == CANCER:
                if random.random() < cancer_kill_rate:
                    grid[row][col] = EMPTY
                elif random.random() < resistance_chance:
                    grid[row][col] = RESISTANT

            elif cell == RESISTANT:
                if random.random() < resistant_kill_rate:
                    grid[row][col] = EMPTY

            elif cell == HEALTHY:
                if random.random() < healthy_kill_rate:
                    grid[row][col] = EMPTY


def count_cells(grid):
    """Count cells and calculate the resistance ratio."""
    healthy_cells = int(np.sum(grid == HEALTHY))
    mutated_cells = int(np.sum(grid == MUTATED))
    cancer_cells = int(np.sum(grid == CANCER))
    resistant_cells = int(np.sum(grid == RESISTANT))
    total_cancer = cancer_cells + resistant_cells

    # resistance_ratio asks:
    # "What fraction of all cancer cells are resistant?"
    if total_cancer > 0:
        resistance_ratio = resistant_cells / total_cancer
    else:
        resistance_ratio = 0

    return {
        "healthy": healthy_cells,
        "mutated": mutated_cells,
        "cancer": cancer_cells,
        "resistant": resistant_cells,
        "total_cancer": total_cancer,
        "resistance_ratio": resistance_ratio,
    }


def step_world(grid):
    """Run one generation."""
    apply_growth(grid)


def add_history_row(history, generation, grid):
    """Store the current cell counts for graphing and CSV export."""
    counts = count_cells(grid)
    counts["gen"] = generation
    history.append(counts)
    return counts


def replace_latest_history_row(history, generation, grid):
    """Update the latest history row after a manual treatment button press."""
    counts = count_cells(grid)
    counts["gen"] = generation

    if history and history[-1]["gen"] == generation:
        history[-1] = counts
    else:
        history.append(counts)

    return counts


# ================================================================
#  DATA OUTPUT
# ================================================================

def save_data_table(history):
    """Save the generation data to a CSV file that can open in Excel."""
    with open("cancer_data.csv", "w") as file:
        file.write(
            "Generation,Healthy,Mutated,Cancer,Resistant,"
            "TotalCancer,ResistanceRatio\n"
        )
        for row in history:
            file.write("{},{},{},{},{},{},{:.3f}\n".format(
                row["gen"],
                row["healthy"],
                row["mutated"],
                row["cancer"],
                row["resistant"],
                row["total_cancer"],
                row["resistance_ratio"],
            ))

    print("Saved data to cancer_data.csv")


def print_summary(history, chemo_doses=0, radiation_doses=0):
    """Print the final result in simple science-fair language."""
    final = history[-1]
    total_cancer = final["total_cancer"]
    resistance_ratio = final["resistance_ratio"]

    takeover_generations = [
        row["gen"]
        for row in history
        if row["resistance_ratio"] > 0.5
    ]

    print("\n=============== FINAL RESULTS ===============")
    print("Final generation          :", final["gen"])
    print("Chemo doses used          :", chemo_doses)
    print("Radiation doses used      :", radiation_doses)
    print("---------------------------------------------")
    print("Healthy cells             :", final["healthy"])
    print("Mutated cells             :", final["mutated"])
    print("Cancer cells              :", final["cancer"])
    print("Resistant cancer cells    :", final["resistant"])
    print("Total cancer cells        :", total_cancer)
    print("Resistance ratio          : {:.3f}".format(resistance_ratio))
    print("---------------------------------------------")

    if total_cancer == 0:
        result = "CONTROLLED: no cancer cells remain in the model"
    elif resistance_ratio > 0.5:
        result = "RESISTANCE TAKEOVER: resistant cancer is dominant"
    elif total_cancer < 50:
        result = "CONTROLLED: cancer is still low"
    else:
        result = "GROWING: cancer is still spreading"

    print("Result                    :", result)

    if takeover_generations:
        print("WARNING: Resistant cancer cells became dominant at least once")
        print("First crossed 50% at generation {}".format(
            takeover_generations[0]))

    print("=============================================")
    print("\nScience meaning:")
    print("Cancer cells grow faster than healthy cells.")
    print("Treatments reduce cancer, but some cells can survive.")
    print("Resistance may exist early or appear after treatment.")
    print("Resistant cells can slowly take over if treatment misses them.")
    print("This helps explain why cancer can return after treatment.")


def plot_resistance_ratio(history, show_window=True):
    """Plot how resistance changes from 0 to 1 over time."""
    if not HAS_GRAPHICS:
        return

    generation_numbers = [row["gen"] for row in history]
    ratios = [row["resistance_ratio"] for row in history]

    plt.figure(figsize=(8, 4))
    plt.plot(
        generation_numbers,
        ratios,
        color="#b10dc9",
        linewidth=2,
        label="Resistance ratio",
    )
    plt.axhline(
        0.5,
        color="#555555",
        linestyle="--",
        linewidth=1.5,
        label="Resistance takeover threshold",
    )
    plt.ylim(0, 1)
    plt.xlabel("Generation")
    plt.ylabel("Resistance ratio")
    plt.title("Treatment Resistance Over Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if show_window:
        plt.show()
    else:
        plt.savefig("resistance_ratio_graph.png")
        plt.close()
        print("Saved graph to resistance_ratio_graph.png")


# ================================================================
#  SIMPLE INTERACTIVE WINDOW
# ================================================================

def make_dashboard_text(generation, counts):
    """Create the small live dashboard at the top of the window."""
    return (
        "Generation: {} / {}     "
        "Healthy: {}     "
        "Cancer: {}     "
        "Resistant: {}"
    ).format(
        generation,
        generations - 1,
        counts["healthy"],
        counts["cancer"],
        counts["resistant"],
    )


def run_with_animation():
    """Run the simple experiment window with only three buttons."""
    grid = make_starting_grid()
    history = []
    chemo_doses = 0
    radiation_doses = 0

    world = {
        "grid": grid,
        "generation": 0,
        "running": False,
        "finished": False,
        "chemo_doses": chemo_doses,
        "radiation_doses": radiation_doses,
        "animation": None,
    }

    counts = add_history_row(history, 0, grid)

    fig = plt.figure(figsize=(9, 8), facecolor="#f4f4f4")
    try:
        fig.canvas.manager.set_window_title("Cancer Cell Experiment")
    except AttributeError:
        pass

    dashboard = fig.text(
        0.5,
        0.95,
        make_dashboard_text(0, counts),
        ha="center",
        va="center",
        fontsize=12,
        weight="bold",
    )

    grid_axis = fig.add_axes([0.08, 0.18, 0.68, 0.68])
    grid_image = grid_axis.imshow(
        grid,
        cmap=cell_colour_map,
        vmin=0,
        vmax=4,
        interpolation="nearest",
    )
    grid_axis.set_title(
        "Simple cancer cell grid",
        fontsize=13,
        pad=10,
    )
    grid_axis.set_xticks([])
    grid_axis.set_yticks([])

    legend_items = [
        Patch(facecolor=cell_colours[HEALTHY], label="green = healthy"),
        Patch(facecolor=cell_colours[MUTATED], label="orange = mutated"),
        Patch(facecolor=cell_colours[CANCER], label="red = cancer"),
        Patch(facecolor=cell_colours[RESISTANT], label="purple = resistant"),
    ]
    fig.legend(
        handles=legend_items,
        loc="center right",
        bbox_to_anchor=(0.98, 0.56),
        frameon=True,
        fontsize=10,
    )

    status_text = fig.text(
        0.5,
        0.12,
        "Press START to begin. Use CHEMO or RADIATION to test treatment.",
        ha="center",
        va="center",
        fontsize=10,
    )

    def refresh_screen(message=None):
        """Redraw grid, dashboard, and short status line."""
        counts_now = count_cells(world["grid"])
        grid_image.set_data(world["grid"])
        dashboard.set_text(
            make_dashboard_text(world["generation"], counts_now)
        )
        if message is not None:
            status_text.set_text(message)
        fig.canvas.draw_idle()
        return counts_now

    def toggle_start_pause(event=None):
        """Start or pause the experiment."""
        if world["finished"]:
            return

        world["running"] = not world["running"]
        if world["running"]:
            start_button.label.set_text("PAUSE")
            status_text.set_text("Running: watch red and purple cells.")
            world["animation"].event_source.start()
        else:
            start_button.label.set_text("START")
            status_text.set_text("Paused.")
            world["animation"].event_source.stop()
        fig.canvas.draw_idle()

    def apply_chemo(event=None):
        """Apply one dose of chemotherapy."""
        world["chemo_doses"] += 1
        apply_treatment(
            world["grid"],
            chemo_cancer_kill_rate,
            chemo_resistant_kill_rate,
            chemo_healthy_kill_rate,
        )
        replace_latest_history_row(
            history,
            world["generation"],
            world["grid"],
        )
        refresh_screen("CHEMO used: tumour should shrink, but some cells may survive.")

    def apply_radiation(event=None):
        """Apply one dose of radiation."""
        world["radiation_doses"] += 1
        apply_treatment(
            world["grid"],
            radiation_cancer_kill_rate,
            radiation_resistant_kill_rate,
            radiation_healthy_kill_rate,
        )
        replace_latest_history_row(
            history,
            world["generation"],
            world["grid"],
        )
        refresh_screen("RADIATION used: cancer is reduced, but resistance can remain.")

    start_axis = fig.add_axes([0.15, 0.035, 0.20, 0.06])
    chemo_axis = fig.add_axes([0.40, 0.035, 0.20, 0.06])
    radiation_axis = fig.add_axes([0.65, 0.035, 0.20, 0.06])

    start_button = Button(start_axis, "START", color="#d9ead3",
                          hovercolor="#ffffff")
    chemo_button = Button(chemo_axis, "CHEMO", color="#ffd6dc",
                          hovercolor="#ffffff")
    radiation_button = Button(radiation_axis, "RADIATION", color="#e6d7ff",
                              hovercolor="#ffffff")

    start_button.on_clicked(toggle_start_pause)
    chemo_button.on_clicked(apply_chemo)
    radiation_button.on_clicked(apply_radiation)

    # Store buttons so matplotlib does not delete them while the window is open.
    world["buttons"] = [start_button, chemo_button, radiation_button]

    def update(frame):
        """Advance the experiment by one generation."""
        if not world["running"] or world["finished"]:
            return [grid_image]

        if world["generation"] >= generations - 1:
            world["running"] = False
            world["finished"] = True
            world["animation"].event_source.stop()
            start_button.label.set_text("DONE")
            refresh_screen("Finished. Close the window to see results and graph.")
            return [grid_image]

        world["generation"] += 1
        step_world(world["grid"])
        counts_now = add_history_row(
            history,
            world["generation"],
            world["grid"],
        )

        if counts_now["resistance_ratio"] > 0.5:
            message = "Warning: resistant cancer is over 50% of the tumour."
        else:
            message = "Running: use treatment and watch the cell counts."

        refresh_screen(message)
        return [grid_image]

    world["animation"] = FuncAnimation(
        fig,
        update,
        interval=animation_speed,
        blit=False,
        cache_frame_data=False,
    )
    world["animation"].event_source.stop()

    plt.show()

    save_data_table(history)
    print_summary(
        history,
        world["chemo_doses"],
        world["radiation_doses"],
    )
    plot_resistance_ratio(history)


# ================================================================
#  FAST MODE FOR TESTING
# ================================================================

def run_fast():
    """Run without a window, using scheduled treatments for a data table."""
    grid = make_starting_grid()
    history = []
    chemo_doses = 0
    radiation_doses = 0

    add_history_row(history, 0, grid)

    for generation in range(1, generations):
        step_world(grid)

        if generation in fast_mode_chemo_generations:
            apply_treatment(
                grid,
                chemo_cancer_kill_rate,
                chemo_resistant_kill_rate,
                chemo_healthy_kill_rate,
            )
            chemo_doses += 1

        if generation in fast_mode_radiation_generations:
            apply_treatment(
                grid,
                radiation_cancer_kill_rate,
                radiation_resistant_kill_rate,
                radiation_healthy_kill_rate,
            )
            radiation_doses += 1

        add_history_row(history, generation, grid)

    save_data_table(history)
    print_summary(history, chemo_doses, radiation_doses)
    plot_resistance_ratio(history, show_window=False)


def main():
    """Choose graphical mode or fast text mode."""
    print("=== Cancer Cell Simulator: educational model only ===")

    if not HAS_NUMPY:
        print("numpy is not installed.")
        print("Install packages with: pip install numpy matplotlib")
    elif "--fast" in sys.argv:
        print("Running fast mode without the button window...")
        run_fast()
    elif not HAS_GRAPHICS:
        print("matplotlib is not installed, so the window cannot open.")
        print("Install packages with: pip install matplotlib")
        print("Running fast mode instead...")
        run_fast()
    else:
        print("Opening the experiment window.")
        print("Press START, then try CHEMO or RADIATION.")
        run_with_animation()


if __name__ == "__main__":
    main()
