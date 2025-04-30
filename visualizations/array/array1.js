console.log("array1.js loaded");

// Data array (initially empty; user input will dictate its contents)
const data = [];

// Dimensions for cells and the SVG
const cellWidth = 80;
const cellHeight = 60;
const cellMargin = 10;
const svgWidth = 600; // Must match the width in index.html

// Select the SVG container
const svg = d3.select("#arraySVG");

// Function to update (or animate) the visualization
function updateVisualization() {
  const visibleData = data;
  const totalWidth = visibleData.length * cellWidth + (visibleData.length - 1) * cellMargin;
  const startX = (svgWidth - totalWidth) / 2;
  const cellY = 50;

  // DATA JOIN
  const cellGroups = svg.selectAll(".cell-group")
    .data(visibleData);

  // EXIT
  cellGroups.exit().remove();

  // ENTER
  const cellEnter = cellGroups.enter()
    .append("g")
      .attr("class", "cell-group")
      .attr("transform", (d, i) => `translate(${startX + i * (cellWidth + cellMargin)},${cellY})`)
      .style("opacity", 0);

  // rectangle
  cellEnter.append("rect")
    .attr("width", cellWidth)
    .attr("height", cellHeight)
    .attr("class", "cell")
    .on("mouseover", function() {
      d3.select(this).transition().duration(200).style("fill", "green");
    })
    .on("mouseout", function() {
      d3.select(this).transition().duration(200).style("fill", "steelblue");
    });

  // value text
  cellEnter.append("text")
    .attr("class", "cell-text")
    .attr("x", cellWidth/2)
    .attr("y", cellHeight/2 + 5)
    .attr("text-anchor", "middle")
    .text(d => d);

  // index text
  cellEnter.append("text")
    .attr("class", "index-text")
    .attr("x", cellWidth/2)
    .attr("y", cellHeight + 20)
    .attr("text-anchor", "middle")
    .text((d, i) => i);

  // MERGE + UPDATE
  cellGroups.merge(cellEnter)
    .transition().duration(500)
    .attr("transform", (d, i) => `translate(${startX + i * (cellWidth + cellMargin)},${cellY})`)
    .style("opacity", 1);
}

// Exposed API for external control
window.visualArray = {
  addElement: function(val) {
    if (typeof val !== 'undefined') {
      data.push(val);
      updateVisualization();
    }
  },
  deleteElement: function(idx) {
    if (Number.isInteger(idx) && idx >= 0 && idx < data.length) {
      data.splice(idx, 1);
      updateVisualization();
    }
  },
  reset: function(newArr) {
    if (Array.isArray(newArr)) {
      data.splice(0, data.length, ...newArr);
      updateVisualization();
    }
  },
  getData: function() {
    return data.slice();
  }
};

// User inputs...
// Add Element handler
d3.select("#addButton").on("click", () => {
  const input = document.getElementById("newElement");
  const newValue = input.value.trim();
  if (newValue !== "") {
    data.push(newValue);
    input.value = "";
    updateVisualization();
  }
});

// Delete Element handler
d3.select("#deleteButton").on("click", () => {
  const idxInput = document.getElementById("delIndex");
  const idx = parseInt(idxInput.value, 10);
  if (!isNaN(idx) && idx >= 0 && idx < data.length) {
    data.splice(idx, 1);
    idxInput.value = "";
    updateVisualization();
  } else {
    alert("Please enter a valid index between 0 and " + (data.length - 1));
  }
});

// Initial render
updateVisualization();
