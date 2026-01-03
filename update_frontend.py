import re

file_path = r'd:\Syllabus Optimizer\webapp\frontend\src\pages\OptimizePage.jsx'

# Compact new sections
new_sections = """
            {/* Objectives */}
            {optimizationResults.optimization?.objectives_optimization?.status==='success'&&(<div className="card"><div className="card-header"><h3 className="card-title">🎯 Objectives Enhancement</h3></div><div style={{padding:'1rem'}}>{optimizationResults.optimization.objectives_optimization.optimized_objectives.map((o,i)=><div key={i} style={{marginBottom:'1rem',padding:'0.5rem',background:'var(--bg-secondary)',borderRadius:'8px'}}><div><strong>Obj {i+1}</strong> <span style={{float:'right',color:'var(--primary)'}}>{o.smart_score}/100</span></div><div style={{fontSize:'0.9rem',marginTop:'0.5rem'}}>Original: {o.original}</div><div style={{fontSize:'0.9rem',color:'var(--success)',marginTop:'0.25rem'}}>Enhanced: {o.optimized}</div></div>)}</div></div>)}

            {/* References */}
            {optimizationResults.optimization?.reference_suggestions?.status==='success'&&(<div className="card"><div className="card-header"><h3 className="card-title">📚 References</h3></div><div style={{padding:'1rem',display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(250px,1fr))',gap:'1rem'}}>{Object.entries(optimizationResults.optimization.reference_suggestions.suggestions||{}).map(([cat,refs])=>refs?.length>0&&<div key={cat}><h4 style={{fontSize:'0.9rem',marginBottom:'0.5rem'}}>{cat.replace(/_/g,' ')}</h4>{refs.slice(0,3).map((r,i)=><div key={i} style={{fontSize:'0.85rem',marginBottom:'0.3rem'}}>• {r.title}</div>)}</div>)}</div></div>)}

            {/* Compliance */}
            {(optimizationResults.optimization?.nep_2020_compliance||optimizationResults.optimization?.accreditation_compliance)&&(<div className="card"><div className="card-header"><h3 className="card-title">🏅 Compliance</h3></div><div style={{padding:'1rem',display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(150px,1fr))',gap:'1rem',textAlign:'center'}}>{optimizationResults.optimization.nep_2020_compliance?.status==='success'&&<div style={{padding:'1rem',background:'var(--bg-secondary)',borderRadius:'8px'}}><div style={{fontSize:'0.9rem',fontWeight:'bold'}}>🇮🇳 NEP 2020</div><div style={{fontSize:'2rem',fontWeight:'bold',color:'var(--primary)',margin:'0.5rem 0'}}>{optimizationResults.optimization.nep_2020_compliance.compliance_percentage}%</div><div style={{fontSize:'0.85rem'}}>{optimizationResults.optimization.nep_2020_compliance.compliance_level}</div></div>}{optimizationResults.optimization.accreditation_compliance?.nba&&<div style={{padding:'1rem',background:'var(--bg-secondary)',borderRadius:'8px'}}><div style={{fontSize:'0.9rem',fontWeight:'bold'}}>NBA</div><div style={{fontSize:'2rem',fontWeight:'bold',color:'var(--primary)',margin:'0.5rem 0'}}>{optimizationResults.optimization.accreditation_compliance.nba.compliance_percentage}%</div><div style={{fontSize:'0.85rem'}}>{optimizationResults.optimization.accreditation_compliance.nba.compliance_level}</div></div>}{optimizationResults.optimization.accreditation_compliance?.naac&&<div style={{padding:'1rem',background:'var(--bg-secondary)',borderRadius:'8px'}}><div style={{fontSize:'0.9rem',fontWeight:'bold'}}>NAAC</div><div style={{fontSize:'2rem',fontWeight:'bold',color:'var(--primary)',margin:'0.5rem 0'}}>{optimizationResults.optimization.accreditation_compliance.naac.compliance_percentage}%</div><div style={{fontSize:'0.85rem'}}>{optimizationResults.optimization.accreditation_compliance.naac.compliance_level}</div></div>}</div></div>)}
"""

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find position - after redundancy closing div, before optimization results closing
    search_text = "              )}\n            )}\n          </div>\n        )}"
    pos = content.find(search_text)
    
    if pos > 0:
        new_content = content[:pos] + new_sections + "\n" + content[pos:]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Frontend updated with new feature sections!")
    else:
        print("❌ Could not find insertion point")
        print("Trying alternative pattern...")
        # Try alternative
        alt = "            )}\n          </div>\n        )}"
        pos2 = content.find(alt)
        if pos2 > 0:
            new_content = content[:pos2] + new_sections + "\n" + content[pos2:]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Frontend updated (alt method)!")
        else:
            print("❌ Could not update - manual edit needed")
            
except Exception as e:
    print(f"❌ Error: {e}")
