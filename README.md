DeepGuardians – AI-Driven Traffic Congestion Prediction and Mobility Optimization System

DeepGuardians is an intelligent transportation system designed to predict traffic congestion patterns and improve urban mobility using machine learning and optimization techniques.

The system uses a Long Short-Term Memory (LSTM) neural network to analyze temporal traffic patterns and predict congestion levels. These predictions are then used by optimization modules such as Travelling Salesman Problem (TSP) based routing, parking intelligence, and departure time recommendations to support efficient travel decisions.

The project follows a branch-based modular development strategy, where each system component is implemented in a separate Git branch.
System Architecture

The DeepGuardians system processes traffic data through multiple modules that collectively produce mobility insights.
Traffic Dataset
      │
      ▼
Data Processing and Feature Engineering
(person1-data-pipeline branch)
      │
      ▼
LSTM Traffic Congestion Prediction
(person1-data-pipeline branch)
      │
      ▼
Route Optimization (TSP)
(traffic modeling modules)
      │
      ▼
Parking Intelligence
(parking-module branch)
      │
      ▼
Departure Time Recommendation
(departure-time-module branch)
      │
      ▼
Mobility Optimization Insights


Branch Modules

The DeepGuardians project follows a branch-based modular development approach. Each branch represents a different module of the system. The traffic dataset is available in all branches so that each module can be developed and tested independently.

main branch

The main branch contains the core repository structure and documentation. It explains the overall system architecture and how the different modules interact within the DeepGuardians system.

person1-data-pipeline branch

This branch contains the data preprocessing pipeline and the LSTM model implementation used for traffic congestion prediction.

The module performs the following tasks:
	•	traffic dataset preprocessing
	•	feature engineering
	•	preparation of time-series sequences for the model
	•	training and testing of the LSTM congestion prediction model

poorva-traffic-model branch

This branch contains traffic modeling experiments and feature analysis related to traffic prediction. It explores modeling approaches and supports the development of the congestion prediction pipeline.

parking-module branch

This branch contains the parking intelligence module.
It focuses on analyzing parking availability and integrating parking information into mobility planning and routing decisions.

departure-time-module branch (planned)

This branch will implement the departure time recommendation module.
The goal of this module is to determine optimal travel start times based on predicted congestion patterns from the LSTM model.

Thank you...
