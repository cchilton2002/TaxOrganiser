import React, { useState } from 'react'
import axios from 'axios';


const Upload = () => {
  const [userId, setUserId] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!userId || !file){
      setMessage("Please enter a user_id and upload a file.");
      return;
    }

    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("file", file);

    try {
      const response = await axios.post("/api/upload", formData);
      setMessage(response.data.message || "Upload successful");

    } catch (err) {
      console.error(err)
      setMessage("Error uploading file.")
    }
  }

  return (
    <div>
      <h2>Upload Payslip</h2>
      <form onSubmit={handleUpload}>
        <input type='text' placeholder='User ID' value={userId} onChange={(e) => setUserId(e.target.value)}/>
        <input type='file' placeholder='File Upload' accept='.pdf' onChange={(e) => setFile(e.target.files[0])}/>
        <button type='submit'>Upload</button>
      </form>
      <p>{message}</p>
    </div>
  )
}

export default Upload
