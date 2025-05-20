import React, { useState } from 'react'
import axios from 'axios';
import MissingPayslipAlert from './MissingPayslipAlert';


const Summary = () => {
  const [userId, setUserId] = useState("");
  const [summary, setSummary] = useState([]);
  const [dates, setDates] = useState([]);
  const [message, setMessage] = useState("");

  const fetchSummary = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.get(`/api/summary?user_id=${userId}`);
      if (response.data.summary || response.data.missing_payslips){
        setSummary(response.data.summary);
        setDates(response.data.missing_payslips);
        setMessage(`Fetched summary for user: ${response.data.user_id}, successfully.`);
        console.log(message)
      } else {
        setSummary([]);
        setDates([]);
        setMessage(response.data.message || `No summary for user: ${response.data.user_id}.`);
      }
    } catch (err) {
      console.error(err);
      setMessage("Error fetching the summary")
    }
  }

  return (
    <div className="p-6 bg-white rounded-xl shadow-md max-w-4xl mx-auto mt-8">
      <h2 className="text-2xl font-semibold text-blue-500 mb-4">Tax Summary</h2>

      <form onSubmit={fetchSummary} className="flex flex-col sm:flex-row items-center gap-4 mb-6">
        <input
          type="text"
          placeholder="Enter User ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="border border-gray-300 rounded-lg px-4 py-2 w-full sm:w-64 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition"
        >
          Get Summary
        </button>
      </form>
      <MissingPayslipAlert missingDates = {dates} />

      {summary.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-300 rounded-lg overflow-hidden">
            <thead className="bg-gray-100">
              <tr>
                <th className="text-left px-4 py-2 border-b">Tax Year</th>
                <th className="text-left px-4 py-2 border-b">Total Gross</th>
                <th className="text-left px-4 py-2 border-b">Total Taxable</th>
                <th className="text-left px-4 py-2 border-b">Total Tax</th>
                <th className="text-left px-4 py-2 border-b">Total NI</th>
              </tr>
            </thead>
            <tbody>
              {summary.map((item, index) => (
                <tr key={index} className="odd:bg-white even:bg-gray-50">
                  <td className="px-4 py-2 border-b">{item.tax_year}</td>
                  <td className="px-4 py-2 border-b">{item.total_gross}</td>
                  <td className="px-4 py-2 border-b">{item.total_taxable}</td>
                  <td className="px-4 py-2 border-b">{item.total_tax}</td>
                  <td className="px-4 py-2 border-b">{item.total_ni}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-gray-500">No data to display.</p>
      )}
    </div>

  )
}

export default Summary
