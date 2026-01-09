const form = document.querySelector("#form")
const input = document.querySelector("#text_input")
const test_pref_buttons = document.querySelector(".test_pref")


form.addEventListener('submit', (event) => {
    event.preventDefault()
    const schoolList = input.value.trim()
    const testPref = document.querySelector("input[type='radio'][name='test']:checked").id
    const schools = schoolList.split(',').map(s => s.trim())

    console.log(schoolList)
    console.log(testPref)
    form.style.display = "none"
    fetchData(schools, testPref)
})

let currentData = null;

async function fetchData(schools, testPref) {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    loading.style.display = 'block';
    results.innerHTML = '';
    
    try {
        const response = await fetch('https://u-fit-college-data-2025.vercel.app/api/schools', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                schools: schools,
                test_pref: testPref  // Send as string '1', '2', or '3'
            })
        });
        
        const data = await response.json();
        currentData = data.data;
        
        if (data.data.length === 0) {
            results.innerHTML = '<p>No data found</p>';
            return;
        }
        
        // Show export button
        document.getElementById('export-btn').style.display = 'inline-block';
        
        // Display results as table
        displayTable(data.data);
        
        // Show skipped schools if any
        if (data.skipped.length > 0) {
            results.innerHTML += `<p style="color: orange;">Unable to find: ${data.skipped.join(', ')}</p>`;
        }
        
    } catch (error) {
        results.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    } finally {
        loading.style.display = 'none';
    }
}

function displayTable(data) {
    const results = document.getElementById('results');
    
    let html = '<table><thead><tr>';
    Object.keys(data[0]).forEach(key => {
        html += `<th>${key}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    data.forEach(school => {
        html += '<tr>';
        Object.values(school).forEach(value => {
            html += `<td>${value}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    results.innerHTML = html;
}

async function exportCSV() {
    if (!currentData) return;
    
    const response = await fetch('https://u-fit-college-data-2025.vercel.app/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: currentData })
    });
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'college_data.csv';
    a.click();
}

