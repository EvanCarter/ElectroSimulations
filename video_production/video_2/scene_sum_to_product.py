from manim import *
import numpy as np


class SumToProductProofScene(Scene):
    """
    Demonstrates WHY sin(theta) + sin(theta + 120) + sin(theta + 240) = 0
    using the sum-to-product trigonometric identity.

    This scene follows ZeroSumStackScene and explains the MATH behind the visual.

    Mathematical flow:
    1. Show the three-term equation with "?"
    2. Introduce sum-to-product identity: sin A + sin B = 2*sin((A+B)/2)*cos((A-B)/2)
    3. Apply to first two terms (sin theta + sin(theta+120))
       - Result: sin(theta + 60)
    4. Apply again to remaining terms (sin(theta+60) + sin(theta+240))
       - cos(-90) = 0 reveal (dramatic)
       - Result: 0

    Visual style:
    - Dark background, clean MathTex typography
    - Color coding: BLUE for A, ORANGE for B, GREEN for C
    - Highlighting/boxing for terms being combined
    - Dramatic reveal when cos(90) = 0
    """

    def construct(self):
        # ============================================================
        # COLORS
        # ============================================================
        COLOR_A = BLUE
        COLOR_B = ORANGE
        COLOR_C = GREEN
        COLOR_HIGHLIGHT = YELLOW
        COLOR_RESULT = WHITE

        # ============================================================
        # STEP 1: SHOW THE FULL EQUATION WITH "?"
        # ============================================================
        main_eq = MathTex(
            r"\sin(\theta)", r"+", r"\sin(\theta + 120^\circ)", r"+", r"\sin(\theta + 240^\circ)", r"=", r"?"
        )
        main_eq[0].set_color(COLOR_A)  # sin(theta)
        main_eq[2].set_color(COLOR_B)  # sin(theta + 120)
        main_eq[4].set_color(COLOR_C)  # sin(theta + 240)
        main_eq[6].set_color(COLOR_HIGHLIGHT)  # ?
        main_eq.scale(0.9)
        main_eq.to_edge(UP, buff=0.8)

        self.play(FadeIn(main_eq))
        self.wait(1.5)

        # ============================================================
        # STEP 2: INTRODUCE SUM-TO-PRODUCT IDENTITY
        # ============================================================
        identity_box = VGroup()

        identity_title = Text("Sum-to-Product Identity:", font_size=28, color=GREY_B)
        identity_formula = MathTex(
            r"\sin A + \sin B = 2 \cdot \sin\left(\frac{A+B}{2}\right) \cdot \cos\left(\frac{A-B}{2}\right)",
            font_size=36
        )

        identity_title.to_edge(LEFT, buff=0.5)
        identity_title.shift(UP * 1.5)
        identity_formula.next_to(identity_title, DOWN, buff=0.3, aligned_edge=LEFT)

        identity_box.add(identity_title, identity_formula)

        # Create a surrounding box
        identity_rect = SurroundingRectangle(identity_box, color=GREY, buff=0.2, corner_radius=0.1)

        self.play(
            FadeIn(identity_title),
            Write(identity_formula),
            run_time=2
        )
        self.play(Create(identity_rect))
        self.wait(1)

        # ============================================================
        # STEP 3: HIGHLIGHT FIRST TWO TERMS
        # ============================================================
        # Create bracket around first two terms in main equation
        first_two_bracket = Brace(VGroup(main_eq[0], main_eq[1], main_eq[2]), DOWN, color=COLOR_HIGHLIGHT)
        first_two_label = Text("Apply identity", font_size=20, color=COLOR_HIGHLIGHT)
        first_two_label.next_to(first_two_bracket, DOWN, buff=0.1)

        self.play(
            GrowFromCenter(first_two_bracket),
            FadeIn(first_two_label)
        )
        self.wait(0.5)

        # ============================================================
        # STEP 4: SHOW SUBSTITUTION AND SIMPLIFICATION
        # ============================================================
        # Position work area below the identity
        work_area_y = -0.5

        # Line 1: Show substitution
        sub_line = MathTex(
            r"A = \theta", r",\quad", r"B = \theta + 120^\circ",
            font_size=32
        )
        sub_line[0].set_color(COLOR_A)
        sub_line[2].set_color(COLOR_B)
        sub_line.move_to([0, work_area_y, 0])

        self.play(Write(sub_line))
        self.wait(0.8)

        # Line 1b: Show explicit arithmetic for numerators
        arith_line = MathTex(
            r"A + B", r"=", r"\theta + (\theta + 120^\circ)", r"=", r"2\theta + 120^\circ",
            font_size=28
        )
        arith_line.move_to([0, work_area_y - 0.7, 0])

        arith_line2 = MathTex(
            r"A - B", r"=", r"\theta - (\theta + 120^\circ)", r"=", r"-120^\circ",
            font_size=28
        )
        arith_line2.next_to(arith_line, DOWN, buff=0.3)

        self.play(Write(arith_line))
        self.wait(0.5)
        self.play(Write(arith_line2))
        self.wait(0.8)

        # Line 2: Initial application
        step1 = MathTex(
            r"\sin(\theta) + \sin(\theta + 120^\circ)",
            r"= 2 \cdot \sin\left(\frac{2\theta + 120^\circ}{2}\right) \cdot \cos\left(\frac{-120^\circ}{2}\right)",
            font_size=28
        )
        step1.move_to([0, work_area_y - 0.8, 0])

        self.play(
            FadeOut(sub_line),
            FadeOut(arith_line),
            FadeOut(arith_line2),
            Write(step1),
            run_time=1.5
        )
        self.wait(0.8)

        # Line 3: Simplify fractions
        step2 = MathTex(
            r"= 2 \cdot \sin(\theta + 60^\circ) \cdot \cos(-60^\circ)",
            font_size=32
        )
        step2.move_to([0, work_area_y - 0.8, 0])

        self.play(Transform(step1, step2))
        self.wait(0.8)

        # Line 4: Highlight cos(-60) = 1/2
        step3 = MathTex(
            r"= 2 \cdot \sin(\theta + 60^\circ) \cdot", r"\frac{1}{2}",
            font_size=32
        )
        step3[1].set_color(COLOR_HIGHLIGHT)
        step3.move_to([0, work_area_y - 0.8, 0])

        cos_note = MathTex(r"\cos(-60^\circ) = \cos(60^\circ) = \frac{1}{2}", font_size=24, color=GREY_B)
        cos_note.next_to(step3, DOWN, buff=0.3)

        self.play(
            Transform(step1, step3),
            FadeIn(cos_note)
        )
        self.wait(0.8)

        # Line 5: Final simplification
        step4 = MathTex(
            r"= \sin(\theta + 60^\circ)",
            font_size=36,
            color=COLOR_RESULT
        )
        step4.move_to([0, work_area_y - 0.8, 0])

        self.play(
            FadeOut(cos_note),
            Transform(step1, step4)
        )
        self.wait(0.5)

        # Box the result
        result1_box = SurroundingRectangle(step1, color=COLOR_HIGHLIGHT, buff=0.15)
        self.play(Create(result1_box))
        self.wait(0.5)

        # ============================================================
        # STEP 5: UPDATE MAIN EQUATION
        # ============================================================
        # Fade out bracket and work, update main equation
        self.play(
            FadeOut(first_two_bracket),
            FadeOut(first_two_label),
            FadeOut(step1),
            FadeOut(result1_box),
        )

        # New main equation with simplified first part
        main_eq_v2 = MathTex(
            r"\sin(\theta + 60^\circ)", r"+", r"\sin(\theta + 240^\circ)", r"=", r"?"
        )
        main_eq_v2[0].set_color(COLOR_RESULT)  # sin(theta + 60)
        main_eq_v2[2].set_color(COLOR_C)  # sin(theta + 240)
        main_eq_v2[4].set_color(COLOR_HIGHLIGHT)  # ?
        main_eq_v2.scale(0.9)
        main_eq_v2.to_edge(UP, buff=0.8)

        self.play(Transform(main_eq, main_eq_v2))
        self.wait(1)

        # ============================================================
        # STEP 6: APPLY IDENTITY AGAIN
        # ============================================================
        # Bracket the two remaining terms
        second_bracket = Brace(VGroup(main_eq_v2[0], main_eq_v2[1], main_eq_v2[2]), DOWN, color=COLOR_HIGHLIGHT)
        second_label = Text("Apply identity again", font_size=20, color=COLOR_HIGHLIGHT)
        second_label.next_to(second_bracket, DOWN, buff=0.1)

        self.play(
            GrowFromCenter(second_bracket),
            FadeIn(second_label)
        )
        self.wait(0.5)

        # Show new substitution
        sub_line2 = MathTex(
            r"A = \theta + 60^\circ", r",\quad", r"B = \theta + 240^\circ",
            font_size=32
        )
        sub_line2.move_to([0, work_area_y, 0])

        self.play(Write(sub_line2))
        self.wait(0.8)

        # Application step
        step2_1 = MathTex(
            r"= 2 \cdot \sin\left(\frac{2\theta + 300^\circ}{2}\right) \cdot \cos\left(\frac{-180^\circ}{2}\right)",
            font_size=28
        )
        step2_1.move_to([0, work_area_y - 0.8, 0])

        self.play(
            FadeOut(sub_line2),
            Write(step2_1),
            run_time=1.5
        )
        self.wait(0.8)

        # Simplify - split into parts so we can highlight cos separately
        step2_2 = MathTex(
            r"= 2 \cdot \sin(\theta + 150^\circ) \cdot", r"\cos(-90^\circ)",
            font_size=32
        )
        step2_2.move_to([0, work_area_y - 0.8, 0])

        self.play(ReplacementTransform(step2_1, step2_2))
        self.wait(0.8)

        # ============================================================
        # STEP 7: THE BIG REVEAL - cos(90) = 0
        # ============================================================
        # Highlight just the cos(-90) term with color animation (no transform)
        self.play(step2_2[1].animate.set_color(COLOR_HIGHLIGHT))
        self.wait(0.5)

        # Create the dramatic reveal
        cos_reveal = MathTex(r"\cos(-90^\circ) = \cos(90^\circ) = 0", font_size=36, color=COLOR_HIGHLIGHT)
        cos_reveal.move_to([0, work_area_y - 1.8, 0])

        # Flash/pulse effect on the reveal
        self.play(
            FadeIn(cos_reveal, scale=1.5),
            Flash(cos_reveal.get_center(), color=COLOR_HIGHLIGHT, line_length=0.3, num_lines=12),
            run_time=1
        )
        self.wait(0.3)

        # Pulse the reveal
        self.play(
            cos_reveal.animate.scale(1.2),
            rate_func=there_and_back,
            run_time=0.5
        )
        self.wait(0.5)

        # Final = 0 (skip the "2·sin·0" step, go straight to result)
        final_zero = MathTex(r"= 0", font_size=48, color=COLOR_HIGHLIGHT)
        final_zero.move_to([0, work_area_y - 0.8, 0])

        self.play(
            Transform(step2_2, final_zero),
            FadeOut(cos_reveal),
            run_time=1
        )
        self.wait(0.5)

        # ============================================================
        # STEP 8: FINAL EQUATION WITH 0
        # ============================================================
        # Clean up
        self.play(
            FadeOut(second_bracket),
            FadeOut(second_label),
            FadeOut(identity_rect),
            FadeOut(identity_title),
            FadeOut(identity_formula),
        )

        # Move zero result up and transform main equation
        final_eq = MathTex(
            r"\sin(\theta)", r"+", r"\sin(\theta + 120^\circ)", r"+", r"\sin(\theta + 240^\circ)", r"=", r"0"
        )
        final_eq[0].set_color(COLOR_A)
        final_eq[2].set_color(COLOR_B)
        final_eq[4].set_color(COLOR_C)
        final_eq[6].set_color(COLOR_HIGHLIGHT)
        final_eq.scale(1.1)
        final_eq.move_to(ORIGIN)

        self.play(
            FadeOut(step2_2),
            FadeOut(main_eq),
            FadeIn(final_eq, scale=1.2),
            run_time=1.5
        )

        # Final box around the complete equation
        final_box = SurroundingRectangle(final_eq, color=COLOR_HIGHLIGHT, buff=0.25, corner_radius=0.1)
        self.play(Create(final_box))

        # Checkmark
        checkmark = MathTex(r"\checkmark", font_size=72, color=GREEN)
        checkmark.next_to(final_box, RIGHT, buff=0.5)
        self.play(FadeIn(checkmark, scale=1.5))

        self.wait(2)
