# JIE42903 TV Scheduling Using Genetic Algorithm

## Files
- `app.py`: Streamlit interface.
- `genetic_algorithm.py`: Genetic Algorithm implementation.
- `program_ratings.csv`: Original lecturer-provided dataset.
- `requirements.txt`: Python dependencies.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Upload all four files to a GitHub repository.
2. Open Streamlit Community Cloud and connect the repository.
3. Select `app.py` as the main file.
4. Deploy.

## Important assignment note
The supplied assignment sheet has conflicting mutation-rate instructions: page 1 specifies a default of 0.2, while page 2 says the mutation rate should be between 0.01 and 0.05. The main interface uses 0.2 as its default, while the three trial controls use 0.01–0.05. Confirm the intended requirement with the lecturer.

The CSV in this starter project is the original dataset and has not been modified. Make and document your chosen rating changes before final submission, as required by the assignment.
