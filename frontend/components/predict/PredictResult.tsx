import { useState } from "react";

export default function PredictResult({ result, imageUrl }: { result: any; imageUrl: string }) {
  const [heatmap, setHeatmap] = useState(false);
  if (!result) return null;

  const plant      = result?.plant      ?? {};
  const prediction = result?.prediction ?? {};
  const toxicity   = result?.toxicity   ?? { level: "unknown", level_code: 3, notes: "" };
  const medicinal  = result?.medicinal  ?? {};
  const gradcam    = result?.gradcam    ?? {};
  const quality    = result?.quality    ?? { passed: false, message: "" };

  const name       = plant?.name            ?? result?.class_name ?? "Unknown";
  const sciName    = plant?.scientific_name ?? "";
  const family     = plant?.family          ?? "";
  const region     = plant?.native_region   ?? "";
  const confidence = prediction?.confidence ?? 0;
  const confLabel  = prediction?.confidence_label ?? "";
  const top3       = prediction?.top3       ?? [];
  const uses       = medicinal?.ayurvedic_uses    ?? [];
  const prep       = medicinal?.preparation       ?? "";
  const compounds  = medicinal?.active_compounds  ?? [];
  const contra     = medicinal?.contraindications ?? [];
  const desc       = medicinal?.description       ?? "";
  const toxLevel   = toxicity?.level      ?? "unknown";
  const toxCode    = toxicity?.level_code ?? 3;
  const toxNotes   = toxicity?.notes      ?? "";

  const confColor = confidence >= 80 ? "#22c55e" : confidence >= 50 ? "#f59e0b" : "#ef4444";
  const toxColor  = ["#22c55e","#f59e0b","#ef4444","#94a3b8"][toxCode] ?? "#94a3b8";

  if (result.success === false) {
    return (
      <div style={{padding:"1.5rem",background:"rgba(239,68,68,.08)",border:"1px solid #ef4444",
                   borderRadius:12,color:"#fca5a5",textAlign:"center"}}>
        <p style={{fontSize:"1rem",fontWeight:600,marginBottom:8}}>Plant not recognised</p>
        <p style={{fontSize:".85rem"}}>{result?.message ?? "Please upload a clear single-leaf photo."}</p>
        {result?.suggestion && <p style={{fontSize:".8rem",marginTop:6,color:"#94a3b8"}}>{result.suggestion}</p>}
      </div>
    );
  }

  return (
    <div style={{border:"1px solid #2d3748",borderRadius:12,overflow:"hidden",background:"#1a1f2e"}}>

      <div style={{position:"relative",height:220}}>
        <img src={heatmap && gradcam?.overlay_base64 ? gradcam.overlay_base64 : imageUrl}
             style={{width:"100%",height:"100%",objectFit:"cover"}} alt="leaf" />
        {gradcam?.overlay_base64 && (
          <button onClick={()=>setHeatmap(!heatmap)}
            style={{position:"absolute",top:10,right:10,background:"rgba(0,0,0,.75)",
                    color:"#fff",border:"none",borderRadius:6,padding:"5px 12px",
                    fontSize:12,cursor:"pointer",fontWeight:500}}>
            {heatmap ? "Original" : "Grad-CAM"}
          </button>
        )}
        <div style={{position:"absolute",bottom:10,left:10,background:"rgba(0,0,0,.75)",
                     borderRadius:6,padding:"4px 10px",fontSize:12,color:confColor,fontWeight:600}}>
          {confidence}% {confLabel}
        </div>
      </div>

      <div style={{padding:"1rem",borderBottom:"1px solid #2d3748"}}>
        <h2 style={{fontSize:"1.2rem",fontWeight:700,color:"#fff",margin:"0 0 2px"}}>{name}</h2>
        {sciName && <p style={{fontSize:".82rem",color:"#64748b",margin:"0 0 4px",fontStyle:"italic"}}>
          {sciName}{family ? ` · ${family}` : ""}
        </p>}
        {!quality.passed && (
          <div style={{background:"rgba(245,158,11,.1)",border:"1px solid #f59e0b",
                       borderRadius:6,padding:"6px 10px",fontSize:".78rem",color:"#fcd34d",margin:"6px 0"}}>
            ⚠ {quality.message}
          </div>
        )}
        {top3.length > 1 && (
          <p style={{fontSize:".75rem",color:"#475569",margin:0}}>
            Also: {top3.slice(1).map((t:any)=>`${t?.name ?? ""} (${t?.confidence ?? 0}%)`).join(" · ")}
          </p>
        )}
      </div>

      <div style={{padding:".75rem 1rem",borderBottom:"1px solid #2d3748",
                   display:"flex",alignItems:"center",gap:8}}>
        <span style={{width:10,height:10,borderRadius:"50%",background:toxColor,flexShrink:0}}/>
        <span style={{fontSize:".85rem",fontWeight:600,color:toxColor,textTransform:"capitalize"}}>
          {toxLevel === "safe" ? "Safe for general use"
         : toxLevel === "caution" ? "Use with caution"
         : toxLevel === "toxic" ? "External use only — toxic if ingested"
         : "Unknown — consult practitioner"}
        </span>
      </div>
      {toxNotes && (
        <div style={{padding:".5rem 1rem",background:"rgba(0,0,0,.2)",fontSize:".74rem",
                     color:"#94a3b8",borderBottom:"1px solid #2d3748"}}>{toxNotes}</div>
      )}

      <div style={{padding:"1rem",display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
        <div>
          <p style={{fontSize:".7rem",fontWeight:600,color:"#4b5563",textTransform:"uppercase",
                     letterSpacing:".06em",marginBottom:6}}>Ayurvedic Uses</p>
          <ul style={{margin:0,paddingLeft:16}}>
            {uses.map((u:string,i:number)=>(
              <li key={i} style={{fontSize:".8rem",color:"#e2e8f0",marginBottom:4,lineHeight:1.4}}>{u}</li>
            ))}
          </ul>
        </div>
        <div>
          <p style={{fontSize:".7rem",fontWeight:600,color:"#4b5563",textTransform:"uppercase",
                     letterSpacing:".06em",marginBottom:6}}>Preparation</p>
          <p style={{fontSize:".8rem",color:"#e2e8f0",lineHeight:1.5,margin:"0 0 6px"}}>{prep}</p>
          {compounds.length > 0 && (
            <p style={{fontSize:".72rem",color:"#64748b",margin:0}}>
              Active: {compounds.join(", ")}
            </p>
          )}
        </div>
      </div>

      {contra.length > 0 && (
        <div style={{padding:".75rem 1rem",borderTop:"1px solid #2d3748",
                     background:"rgba(239,68,68,.05)",fontSize:".78rem",color:"#fca5a5",lineHeight:1.5}}>
          ⚠ Contraindications: {contra.join(" · ")}
        </div>
      )}

      {(desc || region) && (
        <div style={{padding:".75rem 1rem",borderTop:"1px solid #2d3748",
                     fontSize:".77rem",color:"#64748b",lineHeight:1.6}}>
          {desc}
          {region && <span style={{marginLeft:8}}>🌍 {region}</span>}
        </div>
      )}
    </div>
  );
}
