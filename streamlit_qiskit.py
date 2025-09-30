import streamlit as st

import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_vector

from qutip import Bloch


################################################
#### INTRODUCTORY TEXT
################################################

st.header('Walk Around the Bloch')
st.caption("###### Created by Stephen Reagin for PHYS 161, a course in Quantum Information Science at San Jose State University")
st.markdown(r"""
This is a tool for visualizing the *evolution* of the state of a qubit $\ket{\psi}$ as you apply a series of single-qubit quantum gates. 
The qubit is presented as a two-state vector extending from the origin to the surface of a *Bloch sphere*. 
The general formalism can be described as follows:

1. $$ \ket{\psi} = \alpha\ket{0} + \beta\ket{1} =  \begin{bmatrix} \alpha \\ \beta \end{bmatrix} $$ 
    * where $$\|\alpha\|^{2} + \|\beta\|^{2} = 1$$

###### THIS IS MATHEMATICALLY EQUIVALENT TO:

2. $$\ket{\psi} = \cos{\frac{\theta}{2}}\ket{0} + \sin{\frac{\theta}{2}}e^{i\phi}\ket{1}$$ 
    * where $$(r=1, \theta, \phi)$$ are the coordinates of a unit sphere

Quantum logic gates are written as a 2x2 matrix acting on a single qubit state vector $\ket{\psi}$. 
These are always *unitary* gates, meaning they preserve the [unit] length of the vector, and so they can be thought of as a *rotation* in some space.
The Bloch sphere helps us visualize the effects of such unitary gate rotations.

""")

st.markdown(r"""
    ### How to Use

You are given a qubit on the Bloch sphere below, initialized to the state $\ket{\psi}=\ket{0}$ which points to the "north pole" of the sphere.

Rotate the state vector using one of the canonical gates, or input your own angles into the rotation gates. 
As you add more gates you can see a trail blue dots representing your past positions.

Below the Bloch sphere you can also see:
* The final state vector coefficients for $$\ket{\psi} = \alpha\ket{0} + \beta\ket{1}$$
* The total radial "distance" your state vector has traced across the sphere surface
* The "quantum circuit" i.e. the series of gates you applied
* A button to reset everything, because *of course* we want to do it again!

    """)


st.caption("Enough talk, let's start clicking!")
st.divider()


################################################
#### FUNCTIONS
################################################

# This function returns multiple variables:
# 1) The (x,y,z) coordinates of the Bloch vector, given some quantum circuit
# 2) The alpha and beta coefficients solving |x> = a|0> + b|1>

def get_xyz(qc):
    sv = Statevector.from_instruction(qc)
    alpha, beta = sv.data[0], sv.data[1]
    
    x = 2 * np.real(alpha * np.conjugate(beta))
    y = 2 * np.imag(beta * np.conjugate(alpha))
    z = np.abs(alpha)**2 - np.abs(beta)**2
    
    return [x,y,z], alpha, beta


# this function returns the value of Theta between vector iterations
def get_theta(iter_pnt_list):
    a = iter_pnt_list[-1]
    b = iter_pnt_list[-2]
    
    return np.arccos(np.inner(a,b))


#this function resets the app to default settings
def reset_function():
    st.session_state.qc = QuantumCircuit(1)
    qc = st.session_state.qc
    st.session_state.pnt_list = [[0.0, 0.0, 1.0]]
    st.session_state.theta_dist = 0

################################################
#### GATES IN MARKDOWN
################################################

hadamard_text = r"""$H= \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & 1 \end{pmatrix} $"""
paulix_text = r"""$X= \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix} $"""
pauliy_text = r"""$Y= \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix} $"""
pauliz_text = r"""$Z= \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix} $"""

rot_text = r"""$R(\theta, \phi)= \begin{pmatrix} cos(\theta/2) & -ie^{-i\phi}sin(\theta/2) \\ -ie^{i\phi}sin(\theta/2) & cos(\theta/2) \end{pmatrix} $"""

phase_text = r"""$P(\theta)= \begin{pmatrix} 1 & 0 \\ 0 & e^{i\theta} \end{pmatrix} $"""

################################################
#### SESSION STATE
################################################

# The "session state" is a Streamlit quirk
# Without it, the entire script will be run top-to-bottom every time you hit a button
# This now allows us to add/append gates without losing previous state information

if "qc" not in st.session_state:
    st.session_state.qc = QuantumCircuit(1)

if "pnt_list" not in st.session_state:
    st.session_state.pnt_list = [[0.0, 0.0, 1.0],[0.0, 0.0, 1.0]]

if 'theta_dist' not in st.session_state:
    st.session_state.theta_dist = 0

qc = st.session_state.qc


################################################
#### BUTTONS FOR QUANTUM GATES
################################################

# Here are the 'standard' gates
st.subheader('Canonical Gates')
st.caption("""Hover your mouse over any of the gate buttons to see the corresponding 2x2 matrix transformation""")
H, X, Y, Z = st.columns(4)
if H.button("Hadamard", width='stretch', help=hadamard_text):
    H.markdown('You added a Hadamard gate')
    qc.h(0) 
if X.button("Pauli X", width='stretch', help=paulix_text):
    X.markdown('You added a Pauli X gate')
    qc.x(0)
if Y.button("Pauli Y", width='stretch', help=pauliy_text):
    Y.markdown('You added a Pauli Y gate')
    qc.y(0)
if Z.button("Pauli Z", width='stretch', help=pauliz_text):
    Z.markdown('You added a Pauli Z gate')
    qc.z(0)

# Here are the rotation gate inputs
st.subheader('Rotations and Phase Shifts')
st.caption("Input angles as degrees (they are converted to radians behind the scenes)")
RotTheta, RotPhi, PhasePhi, nothing_here  = st.columns(4) # "nothing here" because I want to keep 4 columns (to make it look uniform)
RotTheta_num = RotTheta.number_input('Theta (degrees) \n\n-180 < θ < 180', width=200, min_value=-180, max_value=180, value=0)
RotPhi_num = RotPhi.number_input('Phi (degrees) \n\n-360 < ϕ < 360)', width=200, min_value=-360, max_value=360, value=0)
PhasePhi_num = PhasePhi.number_input('Phase (degrees) \n\n-360 < ϕ < 360)', width=200, min_value=-360, max_value=360, value=0)

# Here are the submit buttons for the rotation inputs above
RotateButton, PhaseButton, placeholder1 = st.columns([2,1,1])
if RotateButton.button('Rotate θ around  \n\n cos(φ)x + sin(φ)y axis', width='stretch', help=rot_text):
    qc.r(RotTheta_num * np.pi / 180, RotPhi_num * np.pi / 180, 0)
#if RotateButton.button('Rotate θ', width='stretch'):
#    qc.r(RotTheta_num * np.pi / 180, 0, 0)
if PhaseButton.button('Rotate phase around Z', width='stretch', help=phase_text):
    qc.p(PhasePhi_num * np.pi / 180, 0)



################################################
#### PLOTTING THE BLOCH SPHERE
################################################

bloch_vector, alpha, beta = get_xyz(qc)             # returns the Bloch Vector (Qiskit object) and the alpha/beta coefficients
st.session_state.pnt_list.append(bloch_vector)      # this appends to a running total of previous vector iterations

# instantiate the Bloch vector
b = Bloch(figsize=(2,2))
b.vector_width = 1
b.font_size = 10

# this adds the vector to the Bloch sphere and updates the "prior" points
b.add_vectors(bloch_vector)
pts = np.array(st.session_state.pnt_list).T
b.add_points(pts, meth='s')

# show the figure
b.show()
st.pyplot(b.fig, width='content')


################################################
#### OTHER DATA POINTS
################################################

st.markdown(f"\n#### Final State Vector \n${np.round(alpha,3)}\ket{0} + {np.round(beta,3)}\ket{1}$")
st.caption(r"State vector is $$\ket{\psi} = \alpha\ket{0} + \beta\ket{1}$$ where $$\|\alpha\|^{2} + \|\beta\|^{2} = 1$$")
st.markdown(f"\nProbability of measuring $\ket{0} = {np.real(np.round(alpha * np.conj(alpha),3))}$")
st.markdown(f"\nProbability of measuring $\ket{1} = {np.real(np.round(beta * np.conj(beta),3))}$")


st.session_state.theta_dist += get_theta(st.session_state.pnt_list) 
st.write(f'\n#### Distance Travelled: {np.round(st.session_state.theta_dist, 3)} radians')
st.caption(r"Distance is $$s = \theta \cdot r$$, and $r=1$ (unit length)")

st.markdown("#### The Quantum Circuit")
st.caption("Diagram of circuits goes left-to-right")
st.pyplot(qc.draw('mpl'))


################################################
#### WRAP IT UP
################################################

st.subheader('Reset the Circuit')
if st.button('Reset Circuit (click twice)'):
    reset_function()



st.divider()
st.markdown(r"""## Further Reading

Wikipedia - [Bloch Sphere](https://en.wikipedia.org/wiki/Bloch_sphere) 

IBM Quantum Learning - [Bloch sphere](https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/density-matrices/bloch-sphere#bloch-sphere)

Quantum Approach to Informatics (Stenholm & Suominen) - [free through SJSU library](https://csu-sjsu.primo.exlibrisgroup.com/permalink/01CALS_SJO/tu4ck5/alma991069283223302901)

Quantum Computation and Quantum Information (Nielsen & Chaung) - [get a new one!](https://www.amazon.com/Quantum-Computation-Information-10th-Anniversary/dp/1107002176)

""")

