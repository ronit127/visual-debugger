import React, { useRef } from "react";
// import * as d3 from "d3"; // seems to be needed for visualization purposes

const SVGComponent = () => {
  // like in old code operations are probably gonna be needed
  const svgref = useRef(null); // will be used for direct reference to svg element
  // Visualization stuff here
  return <svg ref={svgref} width={600} height={400}></svg>;
};

export default SVGComponent;
