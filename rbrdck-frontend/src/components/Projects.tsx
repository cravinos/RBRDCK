import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Define the structure of a project
interface Project {
  name: string;
  url: string;
}

const Projects = () => {
  // Use the Project[] type to define the state
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    axios.get('http://localhost:8000/projects')
      .then(response => {
        console.log(response.data.projects);  // Debugging: Print the response data
        setProjects(response.data.projects);
      })
      .catch(error => console.error('Error fetching projects:', error));
  }, []);

  return (
    <div>
      <h1>User Projects</h1>
      <ul>
        {projects.map(project => (
          <li key={project.name}>
            <a href={project.url} target="_blank" rel="noopener noreferrer">
              {project.name}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Projects;
