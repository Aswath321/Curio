export const fetchStudentData = (studentId) => {
    // This simulates an API call - in a real application, 
    // you would replace this with actual API fetch logic
    const allProjectData = [
      {
        Student_ID: "ST101",
        Project_ID: "P001",
        Project_Name: "AI Healthcare Analysis",
        Milestone_Name: "Data Collection",
        Milestone_Status: "Completed",
        Overall_Status: "On Track",
        Overall_Completion_Percentage: 75,
        Update_Date: "2024-03-15",
        Time_Spent: 45,
        Uploaded_Files: 8,
        Next_Deadline: "2024-04-01",
        File_Paths: {
          pdf: [
            "/Users/aswath/Downloads/Trumio.pdf",
            "/path/to/analysis1.pdf"
          ],
          csv: [
            "/path/to/dataset1.csv",
            "/path/to/results1.csv"
          ],
          other: [
            "/path/to/notes.txt",
            "/path/to/image.jpg"
          ]
        },
        milestones: [
          { name: "Project Initiation", status: "completed", completionDate: "2024-01-15" },
          { name: "Requirements Gathering", status: "completed", completionDate: "2024-02-01" },
          { name: "Data Collection", status: "completed", completionDate: "2024-03-15" },
          { name: "Data Analysis", status: "in progress", completionDate: null },
          { name: "Model Development", status: "pending", completionDate: null },
          { name: "Testing and Validation", status: "pending", completionDate: null },
          { name: "Project Closure", status: "pending", completionDate: null }
        ]
      },
      {
        Student_ID: "ST101",
        Project_ID: "P002",
        Project_Name: "AI ChatBot Analysis",
        Milestone_Name: "Model Development",
        Milestone_Status: "In Progress",
        Overall_Status: "On Track",
        Overall_Completion_Percentage: 52,
        Update_Date: "2024-03-15",
        Time_Spent: 32,
        Uploaded_Files: 2,
        Next_Deadline: "2024-04-01",
        File_Paths: {
          pdf: [
            "/path/to/report1.pdf",
            "/path/to/analysis1.pdf"
          ],
          csv: [
            "/path/to/dataset1.csv",
            "/path/to/results1.csv"
          ],
          other: [
            "/path/to/notes.txt",
            "/path/to/image.jpg"
          ]
        },
        milestones: [
          { name: "Project Initiation", status: "completed", completionDate: "2024-01-20" },
          { name: "Requirements Gathering", status: "completed", completionDate: "2024-02-05" },
          { name: "Data Collection", status: "completed", completionDate: "2024-02-25" },
          { name: "Data Preprocessing", status: "completed", completionDate: "2024-03-10" },
          { name: "Model Development", status: "in progress", completionDate: null },
          { name: "Testing and Validation", status: "pending", completionDate: null },
          { name: "Deployment", status: "pending", completionDate: null },
          { name: "Project Closure", status: "pending", completionDate: null }
        ]
      },
      // ... (other projects with similar milestone data)
    ];
  
    return allProjectData.filter(project => project.Student_ID === studentId);
};
  
  export const calculateMetrics = (studentData) => {
    if (!studentData.length) return null;
  
    return {
      totalProjects: new Set(studentData.map(item => item.Project_ID)).size,
      totalTime: studentData.reduce((sum, item) => sum + item.Time_Spent, 0),
      totalFiles: studentData.reduce((sum, item) => sum + item.Uploaded_Files, 0),
      averageCompletion: Math.round(
        studentData.reduce((sum, item) => sum + item.Overall_Completion_Percentage, 0) / 
        studentData.length
      ),
      nextDeadline: studentData
        .map(item => ({ date: new Date(item.Next_Deadline), milestone: item.Milestone_Name }))
        .sort((a, b) => a.date - b.date)[0]
    };
  };
  
  export const getFilesByType = (studentData) => {
    const files = {
      pdf: [],
      csv: [],
      other: []
    };
  
    studentData.forEach(project => {
      if (project.File_Paths) {
        files.pdf.push(...(project.File_Paths.pdf || []));
        files.csv.push(...(project.File_Paths.csv || []));
        files.other.push(...(project.File_Paths.other || []));
      }
    });
  
    return files;
  };


  

  export const fetchPeerData = () => {
    // This is a mock function. In a real application, you would fetch this data from your backend.
    return {
      averageCompletion: 70, // This is the average completion percentage across all peers
      // You can add more peer-related data here as needed
    };
  };