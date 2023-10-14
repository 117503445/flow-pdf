const { MathpixMarkdownModel } = require('mathpix-markdown-it');

const args = process.argv.slice(2);

let inputFilePath = "";
let outputFilePath = "";

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--input" && i + 1 < args.length) {
    inputFilePath = args[i + 1];
  } else if (args[i] === "--output" && i + 1 < args.length) {
    outputFilePath = args[i + 1];
  }
}

console.log(`inputFilePath: ${inputFilePath}, outputFilePath: ${outputFilePath}`);

const fs = require('fs');

const text = fs.readFileSync(inputFilePath, 'utf8');

const options = {
    htmlTags: true,
    width: 750
};
const htmlMM = MathpixMarkdownModel.markdownToHTML(text, options);

fs.writeFileSync(outputFilePath, htmlMM, 'utf8');