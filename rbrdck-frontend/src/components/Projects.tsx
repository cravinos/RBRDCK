import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';

// Define the structure of a project
interface Project {
  name: string;
  url: string;
}

const ProjectsContainer = styled.div`
  padding: 2rem;
  background-color: #f7fafc;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: bold;
  color: #2d3748;
`;

const ProjectList = styled.ul`
  list-style: none;
  padding: 0;
`;

const ProjectItem = styled.li`
  margin-bottom: 1rem;
`;

const ProjectLink = styled.a`
  color: #1a202c;
  text-decoration: none;
  &:hover {
    color: #e53e3e;
  }
`;

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    axios.get('http://localhost:8000/projects')
      .then(response => {
        setProjects(response.data.projects);
      })
      .catch(error => console.error('Error fetching projects:', error));
  }, []);

  return (
    <ProjectsContainer>
      <Title>User Projects</Title>
      <ProjectList>
        {projects.map((project) => (
          <ProjectItem key={project.name}>
            <ProjectLink href={project.url} target="_blank" rel="noopener noreferrer">
              {project.name}
            </ProjectLink>
          </ProjectItem>
        ))}
      </ProjectList>
    </ProjectsContainer>
  );
};

export default Projects;
