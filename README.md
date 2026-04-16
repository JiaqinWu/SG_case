# Community Hubs Dashboard Example

Synthetic example data and a Streamlit demo app for a community hubs case presentation.

## Files
- `hub_master.csv`: 5 hubs with hub-level indicators, Heart/Head/Hands, and CCI
- `respondent_survey.csv`: 500 respondents (100 per hub) with 12 survey items and SC scores
- `programs_monthly.csv`: monthly operations and engagement metrics
- `spatial_context.csv`: micro-area planning / site prioritization data
- `merged_modeling_dataset.csv`: respondent-level merged modeling table
- `dashboard_app.py`: Streamlit app

## Notes
- Data are synthetic but designed to look realistic.
- Bonding / Bridging / Linking are created as mean subscales from 4 survey items each.
- The dashboard includes a SHAP-style explanation demo using a transparent weighted decomposition so you can explain the concept without a heavy ML pipeline.

## Run locally
```bash
streamlit run dashboard_app.py
```