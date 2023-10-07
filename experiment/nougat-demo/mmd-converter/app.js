const { MathpixMarkdownModel } = require('mathpix-markdown-it');


const fs = require('fs');

const text = fs.readFileSync('HotStuff.mmd', 'utf8');

const options = {
    htmlTags: true,
    width: 750
};
const htmlMM = MathpixMarkdownModel.markdownToHTML(text, options);


fs.writeFileSync('HotStuff.html', htmlMM, 'utf8');