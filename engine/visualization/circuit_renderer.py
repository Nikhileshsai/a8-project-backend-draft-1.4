import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

def circuit_to_svg(qc):
    """
    Converts a Qiskit circuit to a high-quality SVG string using Matplotlib.
    Matches the style used in research notebooks (QAOA_MAX_CUT.ipynb).
    """
    try:
        # style='mpl' provides the professional research-grade look.
        # fold=-1 ensures the circuit is drawn in one continuous horizontal line.
        fig = qc.draw(output='mpl', fold=-1)
        
        # Using a higher DPI for clarity, though SVG is vector-based, 
        # some internal MPL elements benefit from consistent scaling.
        buf = io.StringIO()
        fig.savefig(buf, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)
        
        svg_content = buf.getvalue()
        
        # Clean up the string to ensure it starts with the <svg tag
        if "<svg" in svg_content:
            return svg_content[svg_content.find("<svg"):]
        return svg_content
        
    except Exception as e:
        print(f"Critical rendering error: {e}")
        # Return a simple SVG error message instead of ASCII
        return f'''<svg width="400" height="50" xmlns="http://www.w3.org/2000/svg">
            <text x="10" y="30" font-family="Arial" font-size="14" fill="red">
                Error rendering circuit: {str(e)}
            </text>
        </svg>'''
