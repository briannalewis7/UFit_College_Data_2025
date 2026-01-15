const form = document.querySelector("#form")
const input = document.querySelector("#text_input")
const test_pref_buttons = document.querySelector(".test_pref")
let currentData = null
const homeBtn = document.querySelector(".home-btn")
const exportBtn = document.querySelector(".export-btn")
const loader = document.getElementById('loader')
const loading = document.getElementById('loading')
const results = document.getElementById('results')
const title = document.querySelector('.title')
const addBtn = document.querySelector('.add-btn')

homeBtn.addEventListener("click", returnHome)
exportBtn.addEventListener("click", exportCSV)
addBtn.addEventListener('click', addMore)

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

async function fetchData(schools, testPref) {
    loading.style.display = 'block'
    loader.style.display = 'block'
    results.innerHTML = ''

    try {
        const response = await fetch('/api/schools', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                schools: schools,
                test_pref: testPref
            })
        })
            

        const data = await response.json()
        currentData += data.data

        if (data.data.length === 0) {
            results.innerHTML = '<p>No data found</p>'
            return
        }

        // Show export button
        homeBtn.style.display = 'block'
        exportBtn.style.display = 'inline-block'
        title.style.cursor = 'pointer'
        title.addEventListener('click', returnHome)
        addBtn.style.display = 'block'
    
        // Display results as table
        displayTable(data.data)

        // Show skipped schools if any
        if (data.skipped.length > 0) {
            results.innerHTML += `<p style="color: red;">Unable to find: ${data.skipped.join(', ')}</p>`
        }

    } catch (error) {
        results.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`
    } finally {
        loading.style.display = 'none'
        loader.style.display = 'none'
    }
}

function displayTable(data) {
    let html = '<table><thead><tr>'
    Object.keys(data[0]).forEach(key => {
        html += `<th>${key}</th>`
    })
    html += '</tr></thead><tbody>'

    data.forEach(school => {
        html += '<tr>'
        Object.values(school).forEach(value => {
            html += `<td>${value}</td>`
        })
        html += '</tr>'
    })

    html += '</tbody></table>'
    results.innerHTML = html
}

async function exportCSV() {
    if (!currentData) return

    // Fixed: was calling wrong endpoint
    const response = await fetch('/api/export', {  // Changed from /api/schools
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: currentData })  // Fixed: send currentData
    })

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'college_data.csv'
    a.click()
}

function returnHome() {
    homeBtn.style.display = 'none'
    exportBtn.style.display = 'none'
    form.style.display = 'block'
    results.innerHTML = ''
    input.value = ''
    currentData = null
    title.style.cursor = 'default'
    addBtn.style.display = 'none'
}

function addMore() {
    homeBtn.style.display = 'none'
    exportBtn.style.display = 'none'
    addBtn.style.display = 'none'
    form.style.display = 'block'
    results.innerHTML = ''
    input.value = ''
    title.style.cursor = 'default'
    addBtn.style.display = 'none'
}

