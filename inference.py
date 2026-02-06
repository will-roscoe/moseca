import argparse
import glob
from pathlib import Path
import warnings
from pydub import AudioSegment
from app.service.vocal_remover.runner import load_model, separate
from app.service.demucs_runner import separator
import torch


warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", FutureWarning)
warnings.filterwarnings("ignore", module="streamlit")

usage = """usage

D:\Python\Python310\python.exe inference.py -i "E:\willr\Music\Hozier\Hozier - From Eden.flac" -o "tmp2/" -f "vocals:htdemucs_6s,guitar:htdemucs_6s"

"""

def main_custom():
    p = argparse.ArgumentParser()
    p.add_argument("--gpu", "-g", type=int, default=None,help="gpu identifier.")
    p.add_argument("--pretrained_model", "-P", type=str, default="baseline.pth")
    p.add_argument("--input_glob", "-i", required=True,help="a glob string that points to one or more sound files.")
    p.add_argument("--files","-f",type=str,default="vocals,guitar",help="a string identifying the type of output you want. each output/job is delimited by a comma, and has the form <stem>[:<model>]. typically stems can be 'vocals','bass','drums','other' (see model details). models this works for are 'htdemucs_6s' and 'htdemucs'.")
    p.add_argument("--output_dir", "-o", type=str, default="",help="location to output the results to. internal structure resembles <dir>/<model>[/<orig filename>]/<track contents>.mp3.")
    p.add_argument("--full_mode", "-n", default=True,help="set to false to only use vocal remover.")
    p.add_argument("--shifts","-s",type=int,default=10)
    print(f"torch defaults: ver={torch.__version__},dev={torch.cuda.current_device()},name={torch.cuda.get_device_name()},cap={torch.cuda.get_device_capability()}.")
    
    args = p.parse_args()
    
    print(args)
    stems = []
    for f in [f.split(":") for f in args.files.split(",")]:
        stems.append([
            f[0] if f[0] != "all" else None,
            f[1] if len(f)>1 else "htdemucs_6s"
            ])
    print(stems)
    input_files = [f for f in glob.glob(args.input_glob) if any([str(f).endswith(g) for g in ["flac","mp3","wav","ogg"]])]

    print(f"found {len(input_files)} via {args.input_glob}")
    if bool(args.full_mode):
        model, device = load_model(pretrained_model=args.pretrained_model,dev=args.gpu)
        for input_file in input_files:
            separate(
                input=input_file,
                model=model,
                device=device,
                output_dir=args.output_dir,
            )
        audio = AudioSegment.from_file(input_file)
        audio.export(input_file, format="mp3")
    
    for stem, model_name in stems:
        separator(
            tracks=[Path(i) for i in input_files],
            out=Path(args.output_dir),
            model=model_name,
            shifts=args.shifts,
            overlap=0.5,
            stem=stem,
            int24=False,
            float32=False,
            clip_mode="rescale",
            mp3=True,
            mp3_bitrate=320,
            verbose=False,
        )

if __name__ == "__main__":
    
    main_custom()
