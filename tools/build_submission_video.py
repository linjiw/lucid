"""Assemble a CPU-only anonymous video draft from existing figures and replay footage."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/home/linjiw/lucid-sonic/outputs/submission_video_20260907');OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
parts=[]
def render(name,args):
    output=OUT/f'{name}.mp4'
    subprocess.run(['ffmpeg','-y','-v','error',*args,'-an','-c:v','libx264','-threads','2','-preset','fast','-b:v','1500k','-maxrate','2000k','-bufsize','3000k','-pix_fmt','yuv420p','-r','25','-map_metadata','-1',str(output)],check=True)
    parts.append(output)
def card(name,text,duration):
    path=OUT/f'{name}.txt';path.write_text(text)
    render(name,['-f','lavfi','-i',f'color=c=0x12212b:s=1920x1080:r=25:d={duration}','-vf',f'drawtext=fontfile={FONT}:textfile={path}:fontcolor=white:fontsize=46:line_spacing=25:x=100:y=170'])
card('intro','When Training Gets Easier\nRange collapse and tracking drift in humanoid training\n\nSimulation-only diagnostic study; no hardware claim.\nHistorical MuJoCo policies are distinct from R0/R1/R2.\nDisplayed replay draws illustrate behavior; they are not\nthe full 32-draw quantitative panel.',8)
source=ROOT/'site/videos/frontier_story.mp4'
# Show every original tile, one policy panel at a time, at native tile resolution.
for name,x,y in [('no_dr',0,0),('collapsed',1920,0),('fixed',0,614),('never_shrink',1920,614)]:
    caption=OUT/f'{name}_caption.txt';caption.write_text('Historical MuJoCo replay | 8 displayed draws per condition\nTwo scales: 1.5 then 2.0 | No pushes | Original playback speed')
    render(name,['-i',str(source),'-vf',f'crop=1920:614:{x}:{y},pad=1920:1080:0:200:color=0x12212b,drawtext=fontfile={FONT}:textfile={caption}:fontcolor=white:fontsize=32:line_spacing=14:x=70:y=50'])
for name,figure,caption,duration in [
 ('inversion','return_inversion','12 trained runs: return and robustness are inversely ranked.\nNever-shrink is a safeguard; curriculum superiority is not established.',9),
 ('retention','retention_trajectory','One-origin, one-motion development result | All nominal endpoints complete.\nR1 retains within empirical gates; R0/R2 exceed the quality budget.\nR1 adds anchor computation. Second-seed replication remains pending.',12)]:
    path=OUT/f'{name}_caption.txt';path.write_text(caption)
    render(name,['-loop','1','-i',str(ROOT/f'paper/figures/{figure}.png'),'-t',str(duration),'-vf',f'scale=1700:780:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:70:color=white,drawtext=fontfile={FONT}:textfile={path}:fontcolor=black:fontsize=29:line_spacing=12:x=70:y=910'])
card('closing','Two checks a dashboard cannot replace\n\nEvaluate robustness on conditions the curriculum cannot change.\nEvaluate tracking quality relative to the original policy.\n\nEmpirical safeguards, not a general superiority claim.\nNo calibrated recovery or hardware result is shown.',8)
listing=OUT/'concat.txt';listing.write_text(''.join(f"file '{p}'\n" for p in parts))
final=OUT/'diagnostic-video-draft.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-c','copy','-map_metadata','-1','-movflags','+faststart',str(final)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(final)]))
assert float(probe['format']['duration'])<=180 and final.stat().st_size<20_000_000
assert probe['streams'][0]['height']>=480
(OUT/'receipt.json').write_text(json.dumps({'kind':'existing_footage_video_draft','new_simulation':False,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'probe':probe},indent=2)+'\n')
print(final,final.stat().st_size,probe['format']['duration'])
