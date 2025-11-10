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


def save_projects(projects: List[Project]) -> None:
    """Sauvegarde la liste complète des projets dans db.json."""
    with open(DB_PATH, "w") as f:

        json.dump([proj.model_dump() for proj in projects], f, indent=4)


app = FastAPI(title="ProjetAPI", version="1.0.0")


@app.post("/projects", response_model=Project, status_code=201)
def create_project(project_data: ProjectSubmission) -> Project:
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


@app.delete("/projects/{project_id}")
def delete_project(project_id: str) -> dict[str, str]:
    """Supprime un projet par son id.

    Args:
        project_id: L'identifiant unique du projet à supprimer

    Returns:
        dict: Un message de confirmation avec l'id du projet supprimé

    Raises:
        HTTPException: 404 si le projet n'existe pas
    """
    projects = load_projects()

    # Chercher l'index du projet à supprimer
    for i, proj in enumerate(projects):
        if proj.id == project_id:
            # Supprimer et sauvegarder
            del projects[i]
            save_projects(projects)
            return {"message": "Project deleted successfully", "id": project_id}

    # Si on arrive ici, le projet n'a pas été trouvé
    raise HTTPException(
        status_code=404, detail=f"Project with id {project_id} not found"
    )


@app.get("/projects/course/{courseName}", response_model=List[Project])
def get_projects_by_course(courseName: str) -> List[Project]:
    """
    Filtre et retourne tous les projets soumis pour un cours spécifique.
    (Issue #6)

    Args:
        courseName: Le nom du cours à filtrer (ex: B3 Informatique).

    Returns:
        List[Project]: La liste des projets correspondants.
    """
    projects = load_projects()

    # Filtrage des projets
    filtered_projects = [proj for proj in projects if proj.course == courseName]

    # Retourne une liste (FastAPI gère le statut 200 OK,

    return filtered_projects
