import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

function App() {
  const [desiredPosition, setDesiredPosition] = useState('');
  const [transcript, setTranscript] = useState(null);
  const [resume, setResume] = useState(null);
  const [githubProfile, setGithubProfile] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const onDropTranscript = (acceptedFiles) => {
    setTranscript(acceptedFiles[0]);
  };

  const onDropResume = (acceptedFiles) => {
    setResume(acceptedFiles[0]);
  };

  const { getRootProps: getTranscriptProps, getInputProps: getTranscriptInput } = useDropzone({
    onDrop: onDropTranscript,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1
  });

  const { getRootProps: getResumeProps, getInputProps: getResumeInput } = useDropzone({
    onDrop: onDropResume,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('desired_position', desiredPosition);
    formData.append('transcript', transcript);
    formData.append('resume', resume);
    if (githubProfile) {
      formData.append('github_profile', githubProfile);
    }

    try {
      const response = await axios.post('http://localhost:8000/analyze-profile', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(response.data.data);
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred while analyzing the profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          AI Career Path Advisor
        </Typography>

        <Paper sx={{ p: 3, mb: 3 }}>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Desired Position"
                  value={desiredPosition}
                  onChange={(e) => setDesiredPosition(e.target.value)}
                  required
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper
                  {...getTranscriptProps()}
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    cursor: 'pointer',
                    bgcolor: transcript ? '#e3f2fd' : 'background.paper'
                  }}
                >
                  <input {...getTranscriptInput()} />
                  <Typography>
                    {transcript ? transcript.name : 'Drop transcript PDF here'}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper
                  {...getResumeProps()}
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    cursor: 'pointer',
                    bgcolor: resume ? '#e3f2fd' : 'background.paper'
                  }}
                >
                  <input {...getResumeInput()} />
                  <Typography>
                    {resume ? resume.name : 'Drop resume PDF here'}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="GitHub Profile URL (optional)"
                  value={githubProfile}
                  onChange={(e) => setGithubProfile(e.target.value)}
                />
              </Grid>

              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  disabled={loading || !desiredPosition || !transcript || !resume}
                >
                  {loading ? <CircularProgress size={24} /> : 'Analyze Profile'}
                </Button>
              </Grid>
            </Grid>
          </form>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {results && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Profile Analysis
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Experience Level"
                        secondary={results.experience_level}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Education"
                        secondary={results.education}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Skills"
                        secondary={(results.skills || []).join(', ')}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    GitHub Activity
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Repositories"
                        secondary={results.github_data.repositories}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Languages"
                        secondary={(results.github_data.languages || []).join(', ')}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Stars"
                        secondary={results.github_data.stars}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Forks"
                        secondary={results.github_data.forks}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recommendations
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle1" gutterBottom>
                        Courses
                      </Typography>
                      <List>
                        {((results.recommendations.courses || [])).map((course, index) => (
                          <ListItem key={index}>
                            <ListItemText
                              primary={course.title}
                              secondary={
                                <a href={course.url} target="_blank" rel="noopener noreferrer">
                                  View Course
                                </a>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle1" gutterBottom>
                        Internships
                      </Typography>
                      <List>
                        {((results.recommendations.internships || [])).map((internship, index) => (
                          <ListItem key={index}>
                            <ListItemText
                              primary={internship.name}
                              secondary={
                                <a href={internship.url} target="_blank" rel="noopener noreferrer">
                                  View Internship
                                </a>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle1" gutterBottom>
                        Jobs
                      </Typography>
                      <List>
                        {((results.recommendations.jobs || [])).map((job, index) => (
                          <ListItem key={index}>
                            <ListItemText
                              primary={job.name}
                              secondary={
                                <a href={job.url} target="_blank" rel="noopener noreferrer">
                                  View Job
                                </a>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </Box>
    </Container>
  );
}

export default App; 