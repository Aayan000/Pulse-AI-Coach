async function submitEntry(){
    clearErrors();

    const sleep = document.getElementById("sleep").value;
    const water = document.getElementById("water").value;
    const mood = document.getElementById("mood").value;

    let isValid = true;

    if (!sleep) {
        showError('sleepError', 'Sleep hours is required');
        isValid = false;
    }

    else {
        const sleepNum = parseFloat(sleep);
        if (isNaN(sleepNum)) {
            showError('sleepError', 'Please enter a valid number');
            isValid = false;
        }
        
        else if (sleepNum < 0 || sleepNum > 24){
            showError('sleepError', 'Sleep hours must be between 0 and 24');
        }

        else if (sleepNum > 16) {
            showWarning('sleepError', 'That\'s a lot of sleep, are you sure?');
        }
    }

    if (!water) {
        showError('waterError', 'Water intake is required');
        isValid = false;
    }

    else {
        const waterNum = parseFloat(water);
        if (isNaN(waterNum)) {
            showError('waterError', 'Please enter a valid number');
            isValid = false;
        }
        
        else if (waterNum < 0 || waterNum > 10){
            showError('waterError', 'Water intake must be between 0 and 10 litres');
        }

        else if (waterNum > 5) {
            showWarning('waterError', 'That\'s a lot of water, are you sure?');
        }
    }

    if (!mood) {
        showError('moodError', 'Mood rating is required');
        isValid = false;
    }

    else {
        const moodNum = parseFloat(mood);
        if (isNaN(moodNum)) {
            showError('moodError', 'Please enter a valid number');
            isValid = false;
        }
        
        else if (moodNum < 1 || moodNum > 10){
            showError('moodError', 'Mood rating must be between 1 and 5');
        }
    }

    if (!isValid){
        showFormError('Please fix the errors above before submitting');
        return;
    }

    try{
        const submitBtn = document.querySelector('button[onclick="submitEntry()"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Submitting';
        submitBtn.disabled = true;

        const response = await fetch("/add_entry", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                sleep_hours: parseFloat(sleep),
                water_litres: parseFloat(water),
                mood: parseInt(mood)
            })
        });

        // handle non-JSON or error responses gracefully
        if (!response.ok) {
            let data = null;
            try {
                data = await response.json();
            } catch (e) {
                const text = await response.text().catch(() => null);
                console.error('Server error (non-JSON):', text || e);
                showFormError(text || 'Server error occurred');
                return;
            }

            if (data && data.detail) {
                if (Array.isArray(data.detail)) {
                    data.detail.forEach(error => {
                        const field = error.loc && error.loc[1] ? error.loc[1] : null;
                        if (field) showError(`${field}Error`, error.msg);
                    });
                } else {
                    showFormError(data.detail || 'Server error occurred')
                }
            } else {
                showFormError('Failed to submit entry. Please try again')
            }

            return;
        }

        // parse successful JSON response
        const data = await response.json();

        if (data && data.feedback){
            document.getElementById("feedback").innerHTML = 
                data.feedback.map(f => `<p>${f}</p>`).join("");
            showFormSuccess('Entry submitted successfully')
        }

        document.getElementById("sleep").value = '';
        document.getElementById("water").value = '';
        document.getElementById("mood").value = '';

        refreshCharts();
    }

    catch (error) {
        console.error('Error:', error);
        showFormError('Network error. Please check your connection and try again.');
    }

    finally {
        const submitBtn = document.querySelector('button[onclick="submitEntry()"]');
        submitBtn.textContent = 'Submit';
        submitBtn.disabled = false;
    }

}

function refreshCharts(){
    const timestamp = new Date().getTime();

    const sleepChart = document.getElementById("sleepChart")
    sleepChart.src = `/chart/sleep?t=${timestamp}`;

    const waterChart = document.getElementById("waterChart")
    waterChart.src = `/chart/water?t=${timestamp}`;

    const moodChart = document.getElementById("moodChart")
    moodChart.src = `/chart/mood?t=${timestamp}`;
}

function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.textContent = message;
        field.style.color = '#c62828';

        const inputID = fieldId.replace('Error', '');
        const input = document.getElementById(inputID);

        if(input) {
            input.classList.add('error');
        }
    }
}

function showWarning(fieldId, message){
    const field = document.getElementById(fieldId);
    if(field){
        field.textContent = message;
        field.style.color = '#ff8f00';
    }
}

function showFormError(message){
    const errorDiv = document.getElementById('formErrors');
    if(errorDiv){
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';

        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function showFormSuccess(message){
    let successDiv = document.getElementById('formSuccess');
    if(!successDiv){
        successDiv = document.createElement('div');
        successDiv.id = 'formSuccess';
        successDiv.className = 'success-message';
        // insert into the Add Daily Entry card (left panel) if present
        const container = document.querySelector('.left-panel .card') || document.querySelector('.left-panel') || document.body;
        container.insertBefore(successDiv, container.firstChild);
    }

    successDiv.textContent = message;
    successDiv.style.display = 'block';

    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 3000);
}

function clearErrors(){
    document.querySelectorAll('.field-error').forEach(el => {
        el.textContent = '';
    });

    const formErrors = document.getElementById('formErrors');
    if(formErrors) {
        formErrors.style.display = 'none';
    }

    document.querySelectorAll('input.error').forEach(input => {
        input.classList.remove('error');
    });

    const successDiv = document.getElementById('formSuccess');
    if(successDiv){
        successDiv.style.display = 'none'
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const sleepInput = document.getElementById('sleep');
    const waterInput = document.getElementById('water');
    const moodInput = document.getElementById('mood');
    
    if (sleepInput) {
        sleepInput.addEventListener('blur', validateSleep);
        sleepInput.addEventListener('input', function() {
            document.getElementById('sleepError').textContent = '';
            this.classList.remove('error');
        });
    }
    
    if (waterInput) {
        waterInput.addEventListener('blur', validateWater);
        waterInput.addEventListener('input', function() {
            document.getElementById('waterError').textContent = '';
            this.classList.remove('error');
        });
    }
    
    if (moodInput) {
        moodInput.addEventListener('blur', validateMood);
        moodInput.addEventListener('input', function() {
            document.getElementById('moodError').textContent = '';
            this.classList.remove('error');
        });
    }
});

function validateSleep(){
    const sleep = document.getElementById("sleep").value.trim();
    if(sleep){
        const sleepNum = parseFloat(sleep);
        if (isNaN(sleepNum)){
            showError('sleepError', 'Please enter a valid number')
        }

        else if(sleepNum < 0 || sleepNum > 24){
            showError('sleepError', 'Must be between 0 and 24 hours')
        }
    }
}

function validateWater(){
    const water = document.getElementById("water").value.trim();
    if(water){
        const waterNum = parseFloat(water);
        if (isNaN(waterNum)){
            showError('waterError', 'Please enter a valid number')
        }

        else if(waterNum < 0 || waterNum > 10){
            showError('waterError', 'Must be between 0 and 10 litres')
        }
    }
}

function validateMood(){
    const mood = document.getElementById("mood").value.trim();
    if(mood){
        const moodNum = parseInt(mood);
        if (isNaN(moodNum)){
            showError('moodError', 'Please enter a valid number')
        }

        else if(moodNum < 1 || moodNum > 5){
            showError('moodError', 'Must be between 1 and 5')
        }
    }
}


window.onload = function(){
    refreshCharts();
};