# Universal FK/IK Matching Tool (V1)

A universal utility for Maya animators to seamlessly match FK (Forward Kinematics) and IK (Inverse Kinematics) controls.

## Project Idea

The core philosophy of this tool is **"Result-Driven Matching"**.

In many rigging systems, matching FK and IK can be checking because of different axis orientations, controller offsets, or complex parent hierarchies. This tool bypasses those complexities by using the **Blend Joints** (the final result skeleton that drives the mesh) as the absolute source of truth.

- **FK to IK**: The FK controls are rotated to align with the current pose of the Blend Joints.
- **IK to FK**: The IK control is snapped to the end of the Blend chain, and the Pole Vector is calculated mathematically to match the plane formed by the arm/leg, ensuring no "popping" occurs during the switch.

This makes the tool "Universal" because it doesn't rely on specific rig naming conventions or custom script nodes—as long as you have a standard 3-chain setup (FK, IK, Blend), it works.

## What I am Using

This tool is built with performance and precision in mind, utilizing:

*   **Python 3**: The standard scripting language for modern Maya.
*   **Maya API 2.0 (`maya.api.OpenMaya`)**: Used for all heavy lifting regarding spatial calculations.
    *   **Matrix Math**: Instead of simple constraint alignment, we use Matrix Multiplication (`Target World Matrix * Parent Inverse Matrix`) to calculate the precise local values needed for the controls. This ensures functionality even if controls have `Freeze Transformations` applied or different rotation orders.
    *   **Vector Math**: `MVector` is used to calculate the ideal position for the Pole Vector by projecting the elbow/knee vector onto the plane defined by the limb start and end points.
*   **JSON Serialization**: For saving and loading limb presets, allowing rig setups to be shared across scenes or different characters.
*   **Maya Commands (`maya.cmds`)**: For the native, clear user interface and undo/redo chunking.

## How to Use

### 1. Installation
1.  Save `universal_fkik_match.py` to your Maya scripts folder.
2.  Run the following Python code in the Script Editor or save it to a shelf button:
    ```python
    import universal_fkik_match
    universal_fkik_match.show_ui()
    ```

### 2. Configuration (One-time Setup)
You need to tell the tool what constitutes a "Limb".

1.  **Open the Tool**: Provide a `Limb Name` (e.g., `L_Arm`).
2.  **Define Blend Joints**: Select the result/skin joints for the limb (e.g., Shoulder -> Elbow -> Wrist) and click **Load Selected as Blend Chain**.
3.  **Define FK Controls**: Select the corresponding FK controls in the same order and click **Load Selected as FK Controls**.
4.  **Define IK Control**: Select the main IK controller (the wrist/ankle controller) and click **Load Selected as IK Control**.
5.  **Define Pole Vector**: Select the Pole Vector/Elbow controller and click **Load Selected as Pole Vector**.
6.  **Save**: Click **Save This Limb** to add it to your list.
7.  *(Optional)*: Use **Save All Limbs** under the Presets section to save this configuration to a JSON file for future use.

### 3. Matching Animation
Once your limbs are set up, switching is easy:

**If you are in IK mode and want to switch to FK:**
1.  **Keyframe** your IK controls at the current frame.
2.  Click **Match Selected: FK → IK** (Wait, logic check: if you are in IK mode, the Blend joints are following IK. So you want to match FK controls to the Blend joints. That is `FK -> IK` matching? No, usually in tools, "Match FK to IK" means "Move FK controls so they align with where the IK currently is". Since IK drives Blend, this aligns FK to Blend.)
    *   *Correction*: The button creates the pose. Click **Match All FK to IK** (This moves the FK controls to align with the current IK pose).
3.  Keyframe your FK controls.
4.  Switch your rig's FK/IK blend attribute to FK.

**If you are in FK mode and want to switch to IK:**
1.  **Keyframe** your FK controls at the current frame.
2.  Click **Match Selected: IK → FK** (This moves the IK controls to align with the current FK pose).
3.  Keyframe your IK controls.
4.  Switch your rig's FK/IK blend attribute to IK.

### Features
*   **Auto Keyframe**: Optionally key controls immediately after matching.
*   **Undo Support**: All actions are wrapped in a single undo chunk.
*   **Bilingual UI**: Switch between English and Chinese instantly.
