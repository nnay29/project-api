# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import uuid
from typing import List, Optional


# Schémas de Données Pydantic
# ProjectSubmission: Le schéma pour les données entrantes (Issue #1)
class ProjectSubmission(BaseModel):
    studentName: str
    course: str
    githubUrl: str


# Project: Le schéma complet pour un projet stocké (inclut l'ID et le grade)
class Project(ProjectSubmission):
    id: str
    grade: Optional[float] = None
    # Le grade est optionnel lors de la soumission


DB_PATH = "db.json"


def load_projects() -> List[Project]:
    """Charge les données de db.json."""
    try:
        with open(DB_PATH, "r") as f:
            data = json.load(f)

            return [Project(**proj) for proj in data]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:

        print("Erreur: db.json est vide/mal formaté.Retour à une liste vide.")
        return []


def save_projects(projects: List[Project]):
    """Sauvegarde la liste complète des projets dans db.json."""
    with open(DB_PATH, "w") as f:

        json.dump([proj.model_dump() for proj in projects], f, indent=4)


app = FastAPI(title="ProjetAPI", version="1.0.0")


@app.post("/projects", response_model=Project, status_code=201)
def create_project(project_data: ProjectSubmission):
    """
    Soumet un nouveau projet. Génère un ID unique et l'enregistre dans db.json.
    (Issue #1)
    """
    projects = load_projects()

    # Créer le nouvel objet Project avec un ID unique
    new_project = Project(
        id=str(uuid.uuid4()),
        studentName=project_data.studentName,
        course=project_data.course,
        githubUrl=project_data.githubUrl,
    )

    projects.append(new_project)
    save_projects(projects)

    return new_project


# Endpoint PUT /projects/{project_id}/grade (Issue #4)
class GradeUpdate(BaseModel):
    grade: float


@app.put("/projects/{project_id}/grade", response_model=Project)
def update_project_grade(project_id: str, grade_data: GradeUpdate):
    projects = load_projects()

    for project in projects:
        if project.id == project_id:
            project.grade = grade_data.grade
            save_projects(projects)
            return project

    raise HTTPException(status_code=404, detail="Projet non trouvé")
