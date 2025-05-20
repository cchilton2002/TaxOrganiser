import React, { useState } from 'react';

const MissingPayslipAlert = ({missingDates}) => {
    const [ isOpen, setIsOpen] = useState(false);


    if (!missingDates || missingDates.length === 0) return null;
    
    return(
        <div className="bg-red-100 border border-red-400 text-red-700 rounded-lg p-4 mb-6">
            <div className="flex justify-between items-center">
                <h3 className="font-semibold">Missing Payslips Detected!</h3>
                <button onClick={() => setIsOpen(!isOpen)} className="text-sm text-red-600 hover:underline">
                    {isOpen ? 'Hide Details' : 'View Missing Dates'}
                </button>
            </div>
            {isOpen && (
                <ul className="mt-3 list-disc list-inside space-y-1">
                    {missingDates.map((date,id) => (
                        <li key={id}>{date}</li>
                    ))}
                </ul>
            )}
        </div>

    )
}

export default MissingPayslipAlert;