import React, { useState } from 'react'
import axios from 'axios'


const Payslips = () => {
  const [userId, setUserId] = useState('');
  const [payslips, setPayslips] = useState([]);
  const [message, setMessage] = useState('');

  const fetchPayslips = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.get(`/api/payslips?user_id=${userId}`); 
      if (response.data.payslips) {
        setPayslips(response.data.payslips);
        setMessage(`Fetched payslips for user: ${response.data.user_id}, successfully.`);
      } else {
        setPayslips([]);
        setMessage(response.data.message || `No summary for user: ${response.data.user_id}.`);
      }
    } catch (err) {
      console.error(err)
    }
    
  } 
  
  return (
    <div>
      <h2>Payslip Summary</h2>
      <form onSubmit={fetchPayslips} className="flex flex-col sm:flex-row items-center gap-4 mb-6">
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
          Get Payslips
        </button>
      </form>
      {payslips.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {payslips.map((item) => (
            <div key={item.payslip_id} className="border rounded-xl p-4 shadow bg-white">
              <h3 className="text-lg font-semibold text-blue-600 mb-2">
                Payslip #{item.payslip_id}
              </h3>
              <p><strong>Payment Date:</strong> {new Date(item.payment_date).toLocaleDateString('en-GB', {
                day: '2-digit',
                month: 'short',
                year: '2-digit'
              })}</p>
              <p><strong>Uploaded:</strong> {new Date(item.upload_date).toLocaleDateString('en-GB', {
                day: '2-digit',
                month: 'short',
                year: '2-digit'
              })}</p>
            </div>
          ))}
        </div>

      ) : (
        <p>No Payslips to show</p>
      )}
    </div>
  )
}

export default Payslips;
