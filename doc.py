import streamlit as st


def doc_plots():
    st.write(
        """
    Plot several timeseries of relevant quantities.
    Some quantities are calculated w.r.t a 2D line, which can be
    a `transition` or `area_L`.  
    See JuPedSim documentation.

    These lines are extracted from the geometry file.
    
    #### N-T
    For each line, calculate the cumulative number of pedestrians
    ($N$) passing the line at time ($T$).

    #### Flow
    For each line, calculate the flow ($J$) versus time ($T$).
    Given $N$ pedestrians have passed the line in a time duration of $T$, then the flow is calculates as:
    """
    )
    st.latex(
        r"""
    \begin{equation}
    J = \frac{N - 1}{\Delta t}.
    \end{equation}
    """
    )

    st.write(
        """
    #### Distance-Time
    Relation between time and distance to entrance.
    For each person, the Euclidean distance between the current position and the **first** selected entrance
    is calculated.
    The time to entrance is given by the time the person needs to arrive at the entrance.
    """
    )
    st.image(
        "./figs/distance-time.png",
        caption="Relation between time and distance to entrance. Fig.6 in https://doi.org/10.1371/journal.pone.0177328.g006",
    )

    st.write(
        """
    #### Survival
    The time lapses $\delta$ between two consecutive agents passing a line are calculated.
    The value of $\delta$ reflects the sustained time of clogs interrupting the flow.
    This curve shows the probability distribution function
    $$P(t > δ)$$, also known as the survival function,
    which is an indicator of clogging in front of exits.
    """
    )
    st.image(
        "./figs/survival_function.png",
        caption="The survival functions w.r.t door widths. Fig.7 (a) in https://doi.org/10.1016/j.physa.2021.125934",
    )


def doc_jam():
    st.write(
        """
    A pedestrian $i$ is defined as *congested* if its speed at time $t$
    is below a certain threshold $\hat v$: $v_i(t)<\hat v$.  
    Hence, the set of *congested* pedestrians is defined as
    """
    )
    st.latex(
        r"""
    \begin{equation}
    C(t) = \{i |\; v_i(t) < \hat v \}.
    \end{equation}
    """
    )
    st.info(
        """
    Therefore, we define **jam** as a state, where at least
    $\hat n$ pedestrians are *congested* for a certain amount of time $\hat t$.
    """
    )

    st.write(
        """
    To quantify the characteristics of a jammed state we define the following
    quantities:
    
    #### Maximal waiting time

    The maximal waiting time of congested pedestrians is defined
    as the longest time spent in jam
    """
    )

    st.latex(
        r"""
    \begin{equation}
    T_{w} = \max_i  \{\Delta t = t_{i,2}  - t_{i,1} |\; \Delta t > \hat t,  v(t_{i_1}) < \hat v\; {\rm and}\; v(t_{i_2}) > \hat v \}, 
    \end{equation}
    """
    )
    st.write("""where $\hat t$ is the minimal jam duration.""")
    st.write(
        """
    ####  Lifetime of jam
    Considering a minimal number of pedestrians in jam $\hat n$, and the set of congested pedestrians Eq. (1), the longest time period of a jam is
    """
    )
    st.latex(
        r"""
        \begin{equation}
        T_l = \max_{\Delta t}\{\Delta t = t_{i,2}  - t_{i,1} |\; C(t_{i_1}) > \hat n\; {\rm and}\; C(t_{i_2}) < \hat n \}.
        \end{equation}
        """
    )
    st.write(
        """
    ####  Size of jam
    The number of pedestrians in jam during its lifetime is the mean value of the number of congested pedestrians:    
    """
    )
    st.latex(
        r"""
        \begin{equation}
        \mu \{|C(t) |\;  t \in I\},
        \end{equation}
        """
    )
    st.write(
        """where $I$ is the time interval corresponding
    to the lifetime of time. See Eq. (3)."""
    )

    st.write(
        """
    #### Summary of jam parameters
    | Variable    | Notation |
    |--------------|-----------|
    |**Min Jam Speed**  | $\hat v$|
    |**Min Jam Duration** | $\hat t$|
    |**Min Agents in Jam** | $\hat n$|
    """
    )


def doc_speed():
    st.write(
        """
    #### Speed
     The speed can be calculated *from simulation*: in this case
     use in the inifile the option: `<optional_output   speed=\"TRUE\">`.

     Alternatively, the speed can be calculated *from trajectory*
     according to the forward-formula:
     """
    )
    st.latex(
        r"""
    \begin{equation}
    v_i(f) = \frac{x_i(f+df) - x_i(f))}{df},
    \end{equation}
    """
    )
    st.write(
        r"""with $df$ a constant and $v_i(f)$ the speed of pedestrian $i$ at frame $f$."""
    )


def doc_timeseries():
    st.write(
        """
    Time series of the density and the speed are calculated within the measurement area (a square).
    When the option **Profiles** is activated, you can define measurement are by:
    - $x$-position of the center
    - $y$-position of the center
    - side length of the square

    Depending on the frames per seconds of the trajectories, it might be better to increase the sampling rate
    (`sample`) to speed up rendering the plots.
    """
    )


def doc_profile():
    st.write(
        """
    The density and speed profiles show averaged values over time and over space.

    A grid of square cells $c$ with a given size (can be defined by the slider `Grid size`) is created.
    The values of the density and speed are then averaged over the cells over time.

    Different methods can be used: `Classical`, `Gaussian` and `Weidmann`

    #### Weidmann

    Given the Weidmann-formula **[Weidmann1992 Eq. (15)]**:
    """
    )
    st.latex(
        r"""
    \begin{equation}
    v_i = v^0 \Big(1 - \exp\big(\gamma (\frac{1}{\rho_i} - \frac{1}{\rho_{\max}}) \big)  \Big).
    \end{equation}
    """
    )
    st.text("Eq. (1) can be transformed in ")
    st.latex(
        r"""
    \begin{equation}
    \rho_i = \Big(-\frac{1}{\gamma} \log(1 - \frac{v_i}{v^0})+ \frac{1}{\rho_{\max}}\Big)^{-1},
    \end{equation}
    """
    )
    st.write("""where""")
    st.latex(
        r"""\gamma = 1.913\, m^{-2},\; \rho_{\max} = 5.4\, m^{-2}\; \;{\rm and}\; v^0 = 1.34\, m/s."""
    )
    st.write(
        "Based on the speed, from simulation or trajectory, and using Eq. (2) we can calculate the density $\\rho_i$ and hence,"
    )
    st.latex(
        r"""
    \rho_c = \frac{1}{T}\sum_{t=0}^T S_c,
    """
    )
    st.write("where $S_c$ is the sum of $\\rho_i$ in $c$ and $T$ the evcuation time.")
    st.write("""#### Classical  """)
    st.latex(r"""\rho_c = \frac{1}{T}\sum_{t=0}^T \frac{N_c}{A_c},""")
    st.write("where $A_c$  the area of cell $c$ and $N_c$ the number of agents in $c$.")
    st.write(
        """#### Gaussian
For every pedestrian $i$ the density field over the whole geometry is used. The local density $\\rho$ in the system can be defined as 
        """)
    st.latex(r"""
    \begin{equation}
    \rho(\mathbf{r;\mathbf{X}}) = \sum_{i=1}^{N} \delta(\mathbf{r}_i - \mathbf{r}), \quad \rho(\mathbf{r}) = \langle \rho(\mathbf{r}; \mathbf{X}) \rangle,
    \end{equation}
    """)
    st.write(r"""
    where $\textbf{r}$ is the position and $\textbf{X}$ marks a configuration and $\delta(x)$ is approximated by a Gaussian
    """)
    
    st.latex(r"""
    \begin{equation}
    \delta(x) =\frac{1}{\sqrt{\pi} a } \exp[-x^2/a^2].
    \end{equation}
    """
    )
    st.write("Finally, the average of the density per cell is")
    st.latex(r"""\rho_c = \frac{1}{T}\sum_{t=0}^T \rho(\mathbf{r;\mathbf{X}}) ,""")
    st.write(
        """
The speed is calculated from $\\rho_i$ by Eq. (1).
    """
    )
    st.markdown("--------")
    st.write("#### References:")
    st.code(
        "Weidmann1992: U. Weidmann, Transporttechnik der Fussgänger: Transporttechnische Eigenschaften des Fussgängerverkehrs, Literaturauswertung, 1992"
    )


def docs():
    st.write(
        """
        This is an interactive visual tool for explorative analysis and inspection of pedestrian dynamics.
        Show statistics and make plots extracted from [jpscore](https://github.com/jupedsim/jpscore)-simulations and [experimental data](https://ped.fz-juelich.de/db/).

        The input data are trajectories of pedestrians, that can be [jpscore](https://github.com/jupedsim/jpscore)-simulations or [experimental data](https://ped.fz-juelich.de/db/).

        The following features are measured:
        - N-T curves at lines
        - T-D (time-distance) curves at lines (Adrian2020).
        - Flow vs time at lines
        - Survival function at lines
        - Discharge function
        - Jam waiting time (Sonntag2018)
        - Jam life span (Sonntag2018)
        - RSET heatmaps (Schroder2017a)
        - Density and speed heatmaps (Zhang2012)
        - Density and speed time series
        - Different methods for density and speed calculation
        - Plot trajectories and individual plots
        """
    )


def doc_RSET():
    st.write("""
    RSET maps are defined in Schroeder2017 [1] are a spatial representation of the required safe egress time.
    In a regular grid, the time for which, the cell was last occupied by a pedestrian is calculated.

    These maps give insight about the location of potential jam areas.
    More importantly they  highlight the used exits in the scenario.

    [1]: Multivariate methods for life safety analysis in case of fire
    """)
