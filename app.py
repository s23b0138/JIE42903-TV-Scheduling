import streamlit as st
import pandas as pd
from genetic_algorithm import run_genetic_algorithm

st.set_page_config(page_title="TV Scheduling Using Genetic Algorithm", page_icon="📺", layout="wide")

st.title("📺 TV Scheduling Using Genetic Algorithm")
st.write("Generate an 18-hour TV schedule using a Genetic Algorithm and compare parameter settings.")

@st.cache_data
def load_ratings():
    df = pd.read_csv("program_ratings.csv")
    if df.shape[1] != 19:
        raise ValueError("Expected one program-name column and 18 hourly rating columns.")
    program_col = df.columns[0]
    programs = df[program_col].astype(str).tolist()
    rating_columns = list(df.columns[1:])
    ratings = {}
    for _, row in df.iterrows():
        ratings[str(row[program_col])] = [float(row[col]) for col in rating_columns]
    return df, programs, rating_columns, ratings

try:
    source_df, programs, hour_columns, ratings = load_ratings()
except Exception as exc:
    st.error(f"Could not load program_ratings.csv: {exc}")
    st.stop()

st.sidebar.header("Genetic Algorithm Parameters")
crossover_rate = st.sidebar.slider("Crossover Rate (CO_R)", 0.0, 0.95, 0.8, 0.05)
mutation_rate = st.sidebar.slider("Mutation Rate (MUT_R)", 0.01, 0.95, 0.2, 0.01)
generations = st.sidebar.number_input("Generations", min_value=10, max_value=1000, value=100, step=10)
population_size = st.sidebar.number_input("Population Size", min_value=10, max_value=500, value=50, step=10)
seed = st.sidebar.number_input("Random Seed", min_value=0, max_value=999999, value=42, step=1)


if st.button("Generate Schedule", type="primary"):
    schedule, total_rating, history = run_genetic_algorithm(
        ratings,
        generations=int(generations),
        population_size=int(population_size),
        crossover_rate=float(crossover_rate),
        mutation_rate=float(mutation_rate),
        seed=int(seed),
    )
    st.session_state["main_result"] = (schedule, total_rating, history)
    st.session_state["main_parameters"] = (crossover_rate, mutation_rate)

if "main_result" in st.session_state:
    schedule, total_rating, history = st.session_state["main_result"]
    st.subheader("Final Optimal Schedule")
    schedule_df = pd.DataFrame({
        "Time Slot": [f"{hour:02d}:00" for hour in range(6, 24)],
        "Program": schedule,
    })
    st.dataframe(schedule_df, use_container_width=True, hide_index=True)
    st.metric("Total Ratings", f"{total_rating:.2f}")
    st.subheader("Evolution of Best Schedule")
    history_df = pd.DataFrame(history)
    st.line_chart(history_df.set_index("Generation")["Best Rating"])
    st.dataframe(history_df, use_container_width=True, hide_index=True)

st.divider()
st.header("Three Experimental Trials")
st.write("Run three configurations using the same dataset, generation count, population size and seed for a fairer comparison.")

trial_defaults = [
    ("Trial 1", 0.8, 0.02),
    ("Trial 2", 0.6, 0.03),
    ("Trial 3", 0.9, 0.05),
]
trial_configs = []
cols = st.columns(3)
for col, (name, default_co, default_mut) in zip(cols, trial_defaults):
    with col:
        st.subheader(name)
        co = st.slider(f"{name} Crossover Rate", 0.0, 0.95, default_co, 0.05, key=f"{name}_co")
        mut = st.slider(f"{name} Mutation Rate", 0.01, 0.05, default_mut, 0.01, key=f"{name}_mut")
        trial_configs.append((name, co, mut))

if st.button("Run Three Trials"):
    results = []
    for name, co, mut in trial_configs:
        schedule, score, history = run_genetic_algorithm(
            ratings,
            generations=int(generations),
            population_size=int(population_size),
            crossover_rate=float(co),
            mutation_rate=float(mut),
            seed=int(seed),
        )
        results.append({
            "Trial": name,
            "Crossover Rate": co,
            "Mutation Rate": mut,
            "Total Rating": round(score, 4),
            "Schedule": " → ".join(schedule),
            "Schedule Data": schedule,
            "History": history,
        })
    st.session_state["trial_results"] = results

if "trial_results" in st.session_state:
    st.subheader("Trial Comparison")
    results = st.session_state["trial_results"]
    comparison = pd.DataFrame([
        {k: row[k] for k in ["Trial", "Crossover Rate", "Mutation Rate", "Total Rating"]}
        for row in results
    ])
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    for row in results:
        with st.expander(f'{row["Trial"]} | Total rating: {row["Total Rating"]:.4f}'):
            trial_schedule_df = pd.DataFrame({
                "Time Slot": [f"{hour:02d}:00" for hour in range(6, 24)],
                "Program": row["Schedule Data"],
            })
            st.dataframe(trial_schedule_df, use_container_width=True, hide_index=True)
            st.caption(f'Crossover = {row["Crossover Rate"]:.2f} | Mutation = {row["Mutation Rate"]:.2f}')
            st.line_chart(pd.DataFrame(row["History"]).set_index("Generation")["Best Rating"])

st.divider()
with st.expander("View the source dataset"):
    st.dataframe(source_df, use_container_width=True, hide_index=True)
