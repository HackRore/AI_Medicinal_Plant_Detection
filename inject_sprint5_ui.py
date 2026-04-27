with open(r'd:\PROJECT FINAL\frontend\app\predict\PredictClient.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = '''                 {predictMutation.isSuccess && (
                    <div className="mt-8 text-center">
                       <Button 
                         variant="outline" 
                         className="h-16 px-12 rounded-2xl border-white/10 hover:bg-white/5 text-gray-400 font-black uppercase tracking-widest text-[10px]"
                         onClick={() => {
                           predictMutation.reset()
                           setPreview(null)
                           setUploadedImages([])
                         }}
                       >
                         <Sparkles className="h-4 w-4 mr-2" /> Start New Neural Scan
                       </Button>
                    </div>
                 )}'''

new_block = '''                 {predictMutation.isSuccess && (
                    <div className="mt-8 space-y-4">
                       {predictMutation.data?.vision_validation && (
                         <div className={`flex items-center gap-3 p-4 rounded-2xl border text-xs font-bold uppercase tracking-wider ${predictMutation.data.vision_validation.matches_prediction ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-amber-500/10 border-amber-500/30 text-amber-400'}`}>
                           <span>{predictMutation.data.vision_validation.matches_prediction ? '\u2713' : '\u26a0'}</span>
                           <span>Gemini: {predictMutation.data.vision_validation.matches_prediction ? 'Confirmed' : 'Flagged'}</span>
                           <span className="ml-auto opacity-60">{Math.round((predictMutation.data.vision_validation.agreement_score ?? 0.5) * 100)}% agreement</span>
                         </div>
                       )}
                       {!feedbackSent ? (
                         <button onClick={reportMismatch} disabled={feedbackLoading}
                           className="w-full py-3 rounded-2xl border border-red-500/20 bg-red-500/5 hover:bg-red-500/10 text-red-400 text-xs font-bold uppercase tracking-wider transition-all">
                           {feedbackLoading ? 'Sending...' : '\u26a1 Report Wrong ID \u2014 Help Train Our AI'}
                         </button>
                       ) : (
                         <div className="w-full py-3 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 text-emerald-400 text-xs font-bold uppercase tracking-wider text-center">\u2713 Feedback Received!</div>
                       )}
                       <div className="text-center">
                          <Button variant="outline" className="h-16 px-12 rounded-2xl border-white/10 hover:bg-white/5 text-gray-400 font-black uppercase tracking-widest text-[10px]"
                            onClick={() => { predictMutation.reset(); setPreview(null); setUploadedImages([]); setFeedbackSent(false) }}>
                            <Sparkles className="h-4 w-4 mr-2" /> Start New Neural Scan
                          </Button>
                       </div>
                    </div>
                 )}'''

if old_block in content:
    content = content.replace(old_block, new_block, 1)
    with open(r'd:\PROJECT FINAL\frontend\app\predict\PredictClient.tsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: Sprint 5 UI injected')
else:
    print('FAIL: exact block not matched')
    # Print the actual content around that area for debugging
    idx = content.find('mt-8 text-center')
    print(repr(content[idx-50:idx+500]))
