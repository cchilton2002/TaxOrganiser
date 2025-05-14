import React, { useState } from 'react'
import axios from 'axios';


const Summary = () => {
  const [userId, setUserId] = useState("");
  const [summary, setSummary] = useState([]);
  const [message, setMessage] = useState("");

  const fetchSummary = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.get(`/api/summary?user_id=${userId}`);
      if (response.data.summary){
        setSummary(response.data.summary);
        setMessage(`Fetched summary for user: ${response.data.user_id}, successfully.`);
      } else {
        setSummary([]);
        setMessage(response.data.message || `No summary for user: ${response.data.user_id}.`);
      }
    } catch (err) {
      console.error(err);
      setMessage("Error fetching the summary")
    }
  }

  return (
    <div>
      <h2 className='text-blue-400'>Tax Summary</h2>
      <form onSubmit={fetchSummary}>
        <input type='text' placeholder='Enter User ID' value={userId} onChange={(e) => setUserId(e.target.value)}/>
        <button type='submit'>Get Summary</button>
      </form>
      {message && <p>{message}</p>}
      {summary.length > 0 ?(
              <table>
        <thead>
          <tr>
            <th>Tax Year</th>
            <th>Total Gross</th>
            <th>Total Taxable</th>
            <th>Total Tax</th>
            <th>Total NI</th>
          </tr>
        </thead>
        <tbody>
          {summary.map((item, index) => (
            <tr key={index}>
              <td>{item.tax_year}</td>
              <td>{item.total_gross}</td>
              <td>{item.total_taxable}</td>
              <td>{item.total_tax}</td>
              <td>{item.total_ni}</td>
            </tr>
          ))}
        </tbody>
      </table>
      ) : (
        <p>No data to display.</p>
      )}

    </div>
  )
}

export default Summary
