let chartData = {
    labels: [],
    datasets: [{
        label: '# of Values',
        data: [],
        backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)',
        ],
        borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
        ],
        borderWidth: 1
    }]
};


function createChart(type, height = 400){
    const canvasContainer = document.getElementById('canvas-container');
    canvasContainer.innerHTML = '<canvas id="myChart"></canvas>';
    canvasContainer.style.height = '${height}px';
    const ctx = document.getElementById('myChart').getContext('2d');

    return new Chart(ctx, {
        type: type,
        data: chartData,
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Chart Title' // 默认标题
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            onClick: (event, actieElements) =>{
                if(actieElements.length > 0){
                    const { datasetIndex, index } = actieElements[0];
                    removeData(datasetIndex, index);
                }
            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
            hover: {
                mode: 'index',
                intersect: false
            }
        }
    });

}


let myChart = createChart('bar');    // Create inital chart with default height = 400

function addData(){
    const labelInput = document.getElementById('labelInput');
    const dataInput = document.getElementById('dataInput');

    if(labelInput.value && dataInput.value){
        chartData.labels.push(labelInput.value);
        chartData.datasets.forEach((dataset) =>{
            dataset.data.push(dataInput.value);
        });
        myChart.update();
        labelInput.value = '';
        dataInput.value = '';
    }
}


function updateChartType() {
    const selectedType = document.getElementById('chartType').value;
    myChart.destroy();    // Destroy the old chart
    myChart = createChart(selectedType);

}


function removeData(datasetIndex, index){
    if (chartData.labels.length > index){
        chartData.labels.splice(index, 1);
        chartData.datasets[datasetIndex].data.splice(index, 1);
        myChart.update();
    }
}



// 修改 selectDataSource() 函数
function selectDataSource() {
    // 弹出选择框供用户选择数据源
    const selectedDataSource = prompt("Please select a data source: 'water' or 'electric' or 'object");

    // 根据用户选择更新图表标题和数据
    if (selectedDataSource === 'water') {
        updateChartTitle('Water Usage (tons)');
        updateChartData(waterStatistics);
    } else if (selectedDataSource === 'electric') {
        updateChartTitle('Electric Usage (kWh)');
        updateChartData(electricStatistics);
    } else if (selectedDataSource === 'object') {
        updateChartTitle('Object Usage');
        updateChartData(objectStatistics);
    } else {
        alert('Invalid data source selected!');
    }
}

// 更新图表标题
function updateChartTitle(title) {
    myChart.options.plugins.title.text = title;
    myChart.update();
}


// 更新图表数据
function updateChartData(data) {
    // 清空原有数据
    chartData.labels = [];
    chartData.datasets[0].data = [];

    // 将选择的数据源中的数据更新到图表数据中
    for (const month in data) {
        chartData.labels.push(month);
        chartData.datasets[0].data.push(data[month]);
    }
    myChart.update();
}