"""NEXUS agent system: 6 agents + executive supervisor.

Agents (master doc Part 4.2): Signal Scout, Intent Classifier, Account
Scorer, Outreach Writer, Business Brain, Memory Manager, orchestrated by the
Executive Router in ``supervisor.py``. External callers use
``app.agents.interface`` — the stable API surface.
"""
