# Logistics Optimization Engine

A production-oriented Python logistics routing and optimization system built around
graph algorithms, spatial indexing, route optimization, benchmarking, APIs,
automated testing, Docker, and CI/CD.

> **Status:** Production-oriented, Dockerized, and CI-validated

---

## Overview

The Logistics Optimization Engine is an industry-oriented routing and optimization
system designed to study and demonstrate how data structures and algorithms can
support logistics and transportation decision-making.

The system models a simulated logistics network and provides capabilities for:

- Graph-based road-network representation
- Shortest-path routing
- Spatial search
- Route optimization
- Exact and heuristic TSP solving
- Performance and scalability benchmarking
- REST API services
- Interactive Streamlit dashboard
- Automated testing
- Docker-based deployment
- GitHub Actions CI/CD

The project evolved from a core routing engine into a complete application
covering algorithmic infrastructure, optimization, analytics, APIs, visualization,
testing, and deployment.

---

## Key Capabilities

### Routing

- Dijkstra shortest-path algorithm
- A* shortest-path algorithm
- Route correctness validation
- Route distance and path analysis
- Nodes explored and heap-operation tracking

### Graph Representation

- Object-based graph representation
- Compact graph representation
- CSR-based graph representation
- Bidirectional road connectivity
- Graph validation

### Spatial Intelligence

- KD-Tree spatial indexing
- Spatial search
- Nearest-location analysis

### Route Optimization

- Held-Karp exact TSP
- Nearest Neighbor heuristic
- 2-opt route improvement
- 3-opt route improvement
- Exact-versus-heuristic scalability analysis

### Analytics and Benchmarking

- Routing performance benchmarking
- Search-efficiency analysis
- Graph-representation benchmarking
- Large-scale stress testing
- TSP scalability analysis
- API performance testing
- Concurrent API load testing

### Application Layer

- FastAPI routing API
- Interactive Streamlit dashboard
- Route planner
- Network intelligence
- Algorithm analytics
- Optimization analytics
- Route visualization
- System health monitoring

---

## System Architecture

```text
                         Logistics Network
                                |
                                v
                       Graph Construction
                                |
                +---------------+---------------+
                |                               |
                v                               v
        Graph Representation             Spatial Index
                |                               |
                v                               v
         Dijkstra / A*                      KD-Tree
                |                               |
                +---------------+---------------+
                                |
                                v
                       Route Optimization
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
            Held-Karp                  NN / 2-opt / 3-opt
                 |                             |
                 +--------------+--------------+
                                |
                                v
                     Benchmarking & Testing
                                |
                                v
                       Application Services
                         /             \
                        v               v
                   FastAPI          Streamlit
                     API             Dashboard
                        \             /
                         \           /
                          v         v
                         Logistics System