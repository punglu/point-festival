/* 1e-only ROI measurement. Not product code and not a general screen detector. */
const fs = require('fs'); const path = require('path');
const { chromium } = require('../../../../tests/e2e/node_modules/playwright');
const root = __dirname;
const rois = {
  sidebar_logo:[60,40,160,150], active_nav:[10,430,300,90], footer:[0,930,310,130],
  title:[330,35,260,90], date:[980,45,260,100], summary_1:[330,250,380,190],
  table:[330,410,1090,550], row_1:[330,490,1090,95], pagination:[330,840,1090,100], banner:[330,930,1090,130]
};
/* Fixed threshold: pixel differs from the ROI corner background by Euclidean
 * distance >= 18. Annotation and extraction are intentionally limited to the
 * named 1e ROIs; manual checking is required before any CSS conclusion. */
const canonical = path.join(root, 'canonical', 'canonical-original.png');
const implementation = path.join(root, 'implementation', 'implementation.png');
const sha = file => require('crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex');
(async () => {
  const browser = await chromium.launch(); const page = await browser.newPage({ viewport:{width:1448,height:1086} });
  const decode = async file => page.evaluate(async src => { const image=new Image(); image.src=src; await image.decode(); const canvas=document.createElement('canvas'); canvas.width=image.width; canvas.height=image.height; const ctx=canvas.getContext('2d'); ctx.drawImage(image,0,0); return { width:image.width,height:image.height,channels:4 }; }, `data:image/png;base64,${fs.readFileSync(file).toString('base64')}`);
  const [a,b]=await Promise.all([decode(canonical),decode(implementation)]); await browser.close();
  if (a.width!==1448||a.height!==1086||b.width!==1448||b.height!==1086) throw new Error('INPUT_DIMENSION_MISMATCH');
  fs.writeFileSync(path.join(root,'manifests','rendered-pixel-rois.json'), JSON.stringify({dimensions:[1448,1086], threshold:18, rois, decoder:'Playwright Chromium Canvas', inputs:{canonical:{...a,sha256:sha(canonical)},implementation:{...b,sha256:sha(implementation)}}, status:'PNG_DECODE_PASS_VISIBLE_MASK_PENDING'},null,2));
})().catch(error=>{ console.error(error); process.exit(1); });
