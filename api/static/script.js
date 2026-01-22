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
let append = false
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
        // Append or replace currentData
        if (append) {
            currentData = currentData.concat(data.data)
            append = false
        } else {
            currentData = data.data
        }
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
        displayTable(currentData)

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
    document.querySelector('.test_pref').style.display = 'block'
}

function addMore() {
    // homeBtn.style.display = 'none'
    exportBtn.style.display = 'none'
    addBtn.style.display = 'none'
    form.style.display = 'block'
    results.innerHTML = ''
    input.value = ''
    title.style.cursor = 'default'
    addBtn.style.display = 'none'
    document.querySelector('.test_pref').style.display = 'none'
    append = true
}

const SCHOOL_NAME_MAP = {
    "ucla": "University of California Los Angeles",
    "uclosangeles": "University of California Los Angeles",
    "ucb": "University of California Berkeley",
    "ucberkeley": "University of California Berkeley",
    "berkeley": "University of California Berkeley",
    "ucsb": "University of California Santa Barbara",
    "ucsanta barbara": "University of California Santa Barbara",
    "ucsd": "University of California San Diego",
    "ucsandiego": "University of California San Diego",
    "uci": "University of California Irvine",
    "ucirvine": "University of California Irvine",
    "ucd": "University of California Davis",
    "ucdavis": "University of California Davis",
    "ucsc": "University of California Santa Cruz",
    "ucsantacruz": "University of California Santa Cruz",
    "ucr": "University of California Riverside",
    "ucriverside": "University of California Riverside",
    "ucm": "University of California Merced",
    "ucmerced": "University of California Merced",
    "mizzou": "University of Missouri Columbia",
    "unversityofmissouri": "University of Missouri Columbia",
    "mit": "Massachusetts Institute of Technology",
    "caltech": "California Institute of Technology",
    "nyu": "New York University",
    "usc": "University of Southern California",
    "upenn": "University of Pennsylvania",
    "penn": "University of Pennsylvania",
    "pennstate": "Penn State University Park",
    "psu": "Penn State University Park",
    "pitt": "University of Pittsburgh",
    "washu": "Washington University in St. Louis",
    "wustl": "Washington University in St. Louis",
    "uva": "University of Virginia",
    "umich": "University of Michigan",
    "umichigan": "University of Michigan",
    "michigan": "University of Michigan",
    "umass": "University of Massachusetts Amherst",
    "universityofmassachusetts": "University of Massachusetts Amherst",
    "indiana": "Indiana University Bloomington",
    "iu": "Indiana University Bloomington",
    "iowa": "University of Iowa",
    "unc": "University of North Carolina at Chapel Hill",
    "universityofnorthcarolina": "University of North Carolina at Chapel Hill",
    "uchicago": "University of Chicago",
    "chicago": "University of Chicago",
    "gt": "Georgia Institute of Technology",
    "georgiatech": "Georgia Institute of Technology",
    "uga": "University of Georgia",
    "smu": "Southern Methodist University",
    "uiuc": "University of Illinois at Urbana-Champaign",
    "illinois": "University of Illinois at Urbana-Champaign",
    "universityofillinois": "University of Illinois at Urbana-Champaign",
    "uofi": "University of Illinois at Urbana-Champaign",
    "utaustin": "University of Texas at Austin",
    "universityoftexas": "University of Texas at Austin",
    "austin": "University of Texas at Austin",
    "texas": "University of Texas at Austin",
    "tcu": "Texas Christian University",
    "texaschristian": "Texas Christian University",
    "uw": "University of Washington",
    "uwashington": "University of Washington",
    "cwru": "Case Western Reserve University",
    "casewestern": "Case Western Reserve University",
    "uwmadison": "University of Wisconsin Madison",
    "wisconsin": "University of Wisconsin Madison",
    "madison": "University of Wisconsin Madison",
    "universityofwisconsin": "University of Wisconsin Madison",
    "minnesota": "University of Minnesota Twin Cities",
    "universityofminnesota": "University of Minnesota Twin Cities",
    "minn": "University of Minnesota Twin Cities",
    "virginiatech": "Virginia Polytechnic Institute and State University",
    "vatech": "Virginia Polytechnic Institute and State University",
    "loyola": "Loyola University Chicago",
    "mohio": "Miami University",
    "miamiohio": "Miami University",
    "miamiofohio": "Miami University",
    "miamiu": "Miami University",
    "umiami": "University of Miami",
    "miamiflorida": "University of Miami"
}

const schoolNames = [...new Set(Object.values(SCHOOL_NAME_MAP))]
const autocompleteList = document.querySelector('.autocomplete')

let lastInputValue = ''

input.addEventListener('input', (e) => {
    lastInputValue = e.target.value
    fetchSuggestions(e.target.value)
})

function fetchSuggestions(query) {
    // Clear suggestions if query is too short
    const schools = query.split(', ')
    const currentSchool = schools[schools.length - 1].trim()
    // Clear suggestions if current school is too short
    if (!currentSchool || currentSchool.length < 2) {
        autocompleteList.innerHTML = ''
        autocompleteList.style.display = 'none'
        return
    }

    const queryLower = currentSchool.toLowerCase().replace(/\s/g, '')
    const matches = []

    // Check if input matches a key in the map (abbreviations)
    for (const [key, fullName] of Object.entries(SCHOOL_NAME_MAP)) {
        if (key.includes(queryLower) && !matches.includes(fullName)) {
            matches.push(fullName)
        }
    }

    // Also check if input matches part of the full name
    schoolNames.forEach(name => {
        const nameLower = name.toLowerCase().replace(/\s/g, '')
        if (nameLower.includes(queryLower) && !matches.includes(name)) {
            matches.push(name)
        }
    })
    showSuggestions(matches)
}

function showSuggestions(suggestions) {
    if (suggestions.length === 0) {
        autocompleteList.innerHTML = ''
        autocompleteList.style.display = 'none'
        return
    }
    // Create list items for each suggestion
    autocompleteList.innerHTML = suggestions.map(school =>
        `<li class="autocomplete-item">${school}</li>`
    ).join('')

    autocompleteList.style.display = 'block'

    // Add click handlers to each item
    document.querySelectorAll('.autocomplete-item').forEach(item => {
        item.addEventListener('click', () => {
    const parts = lastInputValue.split(',')

    // Replace only the last segment
    parts[parts.length - 1] = ' ' + item.textContent

    input.value = parts.join(',').trim() + ', '

    autocompleteList.innerHTML = ''
    autocompleteList.style.display = 'none'
        })
    })
}


// Hide suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!input.contains(e.target) && !autocompleteList.contains(e.target)) {
        autocompleteList.style.display = 'none'
    }
})

// Hide suggestions when input loses focus (optional)
// input.addEventListener('blur', () => {
//     // Small delay to allow click to register
//     setTimeout(() => {
//         autocompleteList.style.display = 'none'
//     }, 200)
// })