const crypto = require('crypto');

function canonical(o){
  if (o === null || typeof o !== 'object') return o;
  if (Array.isArray(o)) return o.map(canonical);
  return Object.keys(o).sort().reduce((a,k)=>{
    a[k]=canonical(o[k]); return a;
  },{});
}

function hash(obj){
  const copy = JSON.parse(JSON.stringify(obj));
  const canonicalStr = JSON.stringify(canonical(copy));
  return crypto.createHash('sha256').update(canonicalStr).digest('hex');
}

module.exports = { hash };
