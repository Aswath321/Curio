import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ScatterChart, Scatter } from 'recharts';
import { Target, Clock, FileText, AlertCircle, X, BarChart2, Brain, CheckCircle, Circle } from 'lucide-react';
import { fetchStudentData, calculateMetrics, getFilesByType, fetchPeerData } from './studentProject';
import './dashboard.css';
import FilePopup from './FilePopup';  

const StudentProjectDashboard = ({ studentID }) => {
  const [studentId, setStudentId] = useState('');
  const [studentData, setStudentData] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFilePopup, setShowFilePopup] = useState(false);
  const [showAnalysisPopup, setShowAnalysisPopup] = useState(false);
  const [showAIInsightsPopup, setShowAIInsightsPopup] = useState(false);
  const [showMilestonePopup, setShowMilestonePopup] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [files, setFiles] = useState({ pdf: [], csv: [], other: [] });
  const [peerData, setPeerData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (studentID) {
      fetchAllData();
    }
  }, [studentID]);

  const formatDate = (dateString) => {
    if (!dateString) return '';
    
    try {
      // First try parsing the date string
      const date = new Date(dateString);
      
      // Check if the date is valid
      if (isNaN(date.getTime())) {
        return dateString; // Return original string if parsing fails
      }
      
      // Return formatted date
      return date.toLocaleDateString();
    } catch (error) {
      console.error('Error formatting date:', error);
      return dateString; // Return original string if any error occurs
    }
  };

  const fetchAllData = async () => {
    if (!studentID) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const [projectsRes, metricsRes, filesRes, peerDataRes] = await Promise.all([
        fetch(`http://localhost:8000/api/student/${studentID}/projects`),
        fetch(`http://localhost:8000/api/student/${studentID}/metrics`),
        fetch(`http://localhost:8000/api/student/${studentID}/files`),
        fetch(`http://localhost:8000/api/peer-data`)
      ]);
  
      if (!projectsRes.ok || !metricsRes.ok || !filesRes.ok || !peerDataRes.ok) {
        throw new Error('Failed to fetch data');
      }
  
      const [projects, metrics, files, peerData] = await Promise.all([
        projectsRes.json(),
        metricsRes.json(),
        filesRes.json(),
        peerDataRes.json()
      ]);
  
      setStudentData(projects);
      setMetrics(metrics);
      setFiles(files);
      setPeerData(peerData);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const MetricBox = ({ icon: Icon, value, label, color, onClick }) => (
    <div className="metric-box" style={{ '--metric-color': color }} onClick={onClick}>
      <Icon className="metric-icon" />
      <div className="metric-content">
        <div className="metric-value">{value}</div>
        <div className="metric-label">{label}</div>
      </div>
    </div>
  );

  const MilestonePopup = ({ project, onClose }) => {
    const milestones = project.milestones || [];
    
    // Create a Set to store unique milestone names
    const uniqueMilestones = new Set();
  
    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    };
  
    return (
      <div className="milestone-popup-overlay">
        <div className="milestone-popup">
          <div className="milestone-popup-header">
            <h3>{project.Project_Name} Milestones</h3>
            <button className="close-button" onClick={onClose}>
              <X />
            </button>
          </div>
          <div className="milestone-content">
            {milestones.map((milestone, index) => {
              // Check if this milestone name has already been rendered
              if (uniqueMilestones.has(milestone.name)) {
                return null; // Skip rendering if it's a duplicate
              }
              uniqueMilestones.add(milestone.name);
  
              const isCompleted = milestone.status.toLowerCase() === 'completed';
  
              return (
                <div key={index} className="milestone-item">
                  {isCompleted ? (
                    <CheckCircle className="milestone-icon completed" />
                  ) : (
                    <Circle className="milestone-icon pending" />
                  )}
                  <div className="milestone-info">
                    <h4>{milestone.name}</h4>
                    <p>
                      {isCompleted 
                        ? `Completed on ${formatDate(milestone.completionDate)}` 
                        : `Status: ${milestone.status}`}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };
  
  const AnalysisPopup = ({ onClose }) => {
    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

    const projectCompletionData = studentData.map(project => ({
      name: project.Project_Name,
      completion: project.Overall_Completion_Percentage
    }));

    const timeSpentData = studentData.map(project => ({
      name: project.Project_Name,
      time: project.Time_Spent
    }));

    const fileTypeData = [
      { name: 'PDF', value: files.pdf.length },
      { name: 'CSV', value: files.csv.length },
      { name: 'Other', value: files.other.length }
    ];

    const peerComparisonData = [
      { name: 'You', value: metrics.averageCompletion },
      { name: 'Peers', value: peerData.averageCompletion }
    ];

    // Skill Radar chart data
    const skillRadarData = [
      { subject: 'Coding', A: 120, B: 110, fullMark: 150 },
      { subject: 'Documentation', A: 98, B: 130, fullMark: 150 },
      { subject: 'Time Management', A: 86, B: 130, fullMark: 150 },
      { subject: 'Collaboration', A: 99, B: 100, fullMark: 150 },
      { subject: 'Problem Solving', A: 85, B: 90, fullMark: 150 },
      { subject: 'Creativity', A: 65, B: 85, fullMark: 150 },
    ];

    return (
      <div className="analysis-popup-overlay">
        <div className="analysis-popup" style={{ width: '90%', height: '90%', maxWidth: '1200px', padding: '20px', overflowY: 'auto' }}>
          <div className="analysis-popup-header">
            <h3>Detailed Analysis</h3>
            <button className="close-button" onClick={onClose}>
              <X />
            </button>
          </div>
          <div className="analysis-content" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '60px', marginTop: '20px' }}>
            <div className="chart-container">
              <h4>Project Completion</h4>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={projectCompletionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={<CustomXAxisTick />} interval={0} height={60} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="completion" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-container">
              <h4>Time Spent per Project</h4>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={timeSpentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={<CustomXAxisTick />} interval={0} height={60} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="time" stroke="#82ca9d" name="Time (hours)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-container">
              <h4>File Type Distribution</h4>
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={fileTypeData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label
                  >
                    {fileTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-container">
              <h4>Peer Comparison (Average Completion)</h4>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={peerComparisonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-container">
              <h4>Skill Radar</h4>
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={skillRadarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" />
                  <PolarRadiusAxis angle={30} domain={[0, 150]} />
                  <Radar name="You" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                  <Radar name="Average Peer" dataKey="B" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
                  <Legend />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const CustomXAxisTick = ({ x, y, payload }) => {
    return (
      <g transform={`translate(${x},${y})`}>
        <text 
          x={0} 
          y={0} 
          dy={16} 
          textAnchor="end" 
          fill="#666" 
          transform="rotate(-35)"
          style={{fontSize: '12px'}}
        >
          {payload.value}
        </text>
      </g>
    );
  };

  const AIInsightsPopup = ({ onClose }) => {
    return (
      <div className="ai-insights-popup-overlay">
        <div className="ai-insights-popup">
          <div className="ai-insights-popup-header">
            <h3>AI Insights</h3>
            <button className="close-button" onClick={onClose}>
              <X />
            </button>
          </div>
          <div className="ai-insights-content">
            <h4>Performance Overview</h4>
            <p>Based on the analysis of your project data, here are some AI-generated insights:</p>
            <ul>
              <li>Your overall project completion rate is 15% higher than the average of your peers, indicating strong progress.</li>
              <li>Time management could be improved. You're spending 20% more time on tasks compared to successful peers.</li>
              <li>Your file organization is excellent, with a good balance of documentation (PDFs) and data files (CSVs).</li>
            </ul>
            
            <h4>Recommendations</h4>
            <p>To further improve your performance, consider the following suggestions:</p>
            <ol>
              <li>Focus on optimizing your workflow for the "Data Preprocessing" phase, as it's taking longer than expected.</li>
              <li>Collaborate more with peers who have high completion rates to learn their efficient practices.</li>
              <li>Consider breaking down larger tasks into smaller, manageable subtasks to improve overall project velocity.</li>
            </ol>
            
            <h4>Predictive Insights</h4>
            <p>Based on your current progress and historical data:</p>
            <ul>
              <li>You're on track to complete the project 2 days ahead of the deadline if you maintain your current pace.</li>
              <li>There's a 80% chance you'll exceed expectations in the final evaluation, given your attention to comprehensive documentation.</li>
            </ul>
            
            <p>Remember, these insights are generated based on available data and general patterns. Always use your judgment and consult with your instructors for personalized guidance.</p>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="dashboard-container">
      {metrics && (
        <div className="dashboard-content">
          <div className="metrics-grid">
            <MetricBox
              icon={Target}
              value={`${metrics.averageCompletion}%`}
              label="Overall Completion"
              color="#10b981"
            />
            <MetricBox
              icon={Clock}
              value={`${metrics.totalTime}h`}
              label="Total Time Spent"
              color="#3b82f6"
            />
            <MetricBox
              icon={FileText}
              value={metrics.totalFiles}
              label="Files Uploaded"
              color="#8b5cf6"
              onClick={() => setShowFilePopup(true)}
            />
            <MetricBox
              icon={BarChart2}
              value="Analyze"
              label="Further Analysis"
              color="#f97316"
              onClick={() => setShowAnalysisPopup(true)}
            />
            <MetricBox
              icon={Brain}
              value="Insights"
              label="AI Insights"
              color="#ec4899"
              onClick={() => setShowAIInsightsPopup(true)}
            />
          </div>

          <div className="timeline-section">
            <h2 className="section-title">Project Timeline</h2>
            <div className="timeline-container">
              {studentData.map((project, index) => (
                <div 
                  key={index} 
                  className="timeline-item"
                  onClick={() => {
                    setSelectedProject(project);
                    setShowMilestonePopup(true);
                  }}
                >
                  <div className="timeline-status">
                    <div className={`status-dot ${project.Milestone_Status.toLowerCase()}`} />
                  </div>
                  <div className="timeline-content">
                    <div className="timeline-header">
                      <h3>{project.Project_Name}</h3>
                      <span className="timeline-date">{formatDate(project.Update_Date)}</span>
                    </div>
                    <div className="timeline-details">
                      <p className="milestone">{project.Milestone_Name}</p>
                      <p className="status">Status: {project.Overall_Status}</p>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill"
                          style={{ width: `${project.Overall_Completion_Percentage}%` }}
                        />
                      </div>
                      <div className="timeline-metrics">
                        <span><Clock className="inline-icon" /> {project.Time_Spent}h</span>
                        <span><FileText className="inline-icon" /> {project.Uploaded_Files} files</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {metrics.nextDeadline && (
            <div className="deadline-alert">
              <AlertCircle className="alert-icon" />
              <span>Next Deadline: {metrics.nextDeadline.milestone} due on {formatDate(metrics.nextDeadline.date)}</span>
            </div>
          )}
        </div>
      )}

      {showFilePopup && <FilePopup onClose={() => setShowFilePopup(false)} files={files} />}
      {showAnalysisPopup && <AnalysisPopup onClose={() => setShowAnalysisPopup(false)} />}
      {showAIInsightsPopup && <AIInsightsPopup onClose={() => setShowAIInsightsPopup(false)} />}
      {showMilestonePopup && selectedProject && (
        <MilestonePopup 
          project={selectedProject} 
          onClose={() => setShowMilestonePopup(false)} 
        />
      )}
    </div>
  );
};

export default StudentProjectDashboard;