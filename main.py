from manim import * # v0.19.0
import svgelements as se

class LfsrScene(Scene):
	def construct(self):
		self.bit_squares = VGroup(Square(side_length=.75) for _ in range(16)).set_x(0).arrange(buff=0)
		xor_gate = VMobjectFromSVGPath(se.Path("""m 0,0
		   c 0,0 -10,0 -17,10  7,10 17,10 17,10
           h 13
           c -5,-5 -5,-15 0,-20
           z
           m 17,20
           c -5,-5 -5,-15 0,-20""")).scale(.05).move_to((3, -1, 0))
		self.bit7_line = DashedLine((.365, -1, 0), (.365, -.365, 0))

		self.play(LaggedStart(
			*[Create(bit_sq) for bit_sq in self.bit_squares],
			Create(xor_gate),
			Create(Circle(radius=.15, color="#FFF").move_to((2, -1, 0))),
			Create(Line((5.625, -.365, 0), (5.625, -1.25, 0))),
			Create(Line((4.855, -.365, 0), (4.855, -.75, 0))),
			Create(Line((1.87, -1, 0), (-5.625, -1, 0))),
			Create(Line((5.625, -1.25, 0), (3.71, -1.25, 0))),
			Create(Line((4.855, -.75, 0), (3.71, -.75, 0))),
			Create(Line((-5.625, -1, 0), (-5.625, -.365, 0))),
			Create(self.bit7_line),
			run_time=2,
		))

		self.bits = None
		self.short = False

	def set_short(self, short):
		if self.short == short:
			pass
		else:
			self.short = short
			text = Text("short\nmode" if short else "long\nmode", color="#aaa", font_size=30, should_center=True).next_to(self.bit7_line, DOWN)
			self.play(FadeIn(text))
			if short:
				self.play(FadeOut(text), self.bit7_line.animate.become(Line((.365, -1, 0), (.365, -.365, 0))))
			else:
				self.play(FadeOut(text), self.bit7_line.animate.become(DashedLine((.365, -1, 0), (.365, -.365, 0))))

	def trigger(self):
		trigger_text = Text("trigger", color="#aaa", font_size=30).next_to(self.bit_squares, UP)

		fadein = [FadeIn(trigger_text, run_time=.5)]
		if self.bits is not None:
			fadein.append(FadeOut(Group(*self.bits)))
		self.play(*fadein)
		self.bits = [Text("0", font_size=40) for _ in range(16)]
		bits = VGroup(*self.bits).set_x(0).arrange(buff=.47)
		self.play(FadeIn(bits), FadeOut(trigger_text))

	def step(self, individual_run_time=.25):
		text = Text("step", color="#aaa", font_size=30).next_to(self.bit_squares, UP)
		self.play(FadeIn(text, run_time=individual_run_time))

		bit0 = self.bits[15].copy() # The array goes left-to-right!
		bit1 = self.bits[14].copy()
		self.play(
			bit0.animate(run_time=individual_run_time).set_color("#f84"),
			bit1.animate(run_time=individual_run_time).set_color("#f84"),
		)
		self.play(
			bit0.animate(run_time=individual_run_time).move_to((5.625, -1.25, 0)),
			bit1.animate(run_time=individual_run_time).move_to((4.855, -.75, 0)),
		)

		def bit(bool, text):
			if bool:
				return Text(text[1], font_size=40, color="#4f4")
			else:
				return Text(text[0], font_size=40, color="#f44")
		equal = bit(bit0.text != bit1.text, ["=", "≠"]).move_to((3, -1, 0))
		self.play(
			FadeIn(equal, target_position=(4, -1, 0), run_time=individual_run_time),
			FadeOut(bit0, target_position=(4, -1.25, 0), run_time=individual_run_time),
			FadeOut(bit1, target_position=(4, -.75, 0), run_time=individual_run_time),
		)
		self.play(equal.animate(run_time=individual_run_time).become(
			bit(bit0.text != bit1.text, ["0", "1"])
				.move_to((equal.get_x(), equal.get_y(), equal.get_z()))
		))
		self.play(equal.animate(run_time=individual_run_time).become(
			bit(bit0.text == bit1.text, ["0", "1"]).move_to((1.5, -1, 0))
		))
		bits = [equal]
		if self.short:
			bits.append(equal.copy())
		self.play(bit.animate(run_time=individual_run_time).move_to((x, -1, 0)) for bit,x in zip(bits, [-5.625, .365]))
		self.play(bit.animate(run_time=individual_run_time).move_to((bit.get_x(), 0, 0)) for bit in bits)
		self.play(
			LaggedStart(
				FadeOut(self.bits[i], run_time=individual_run_time),
				bit.animate(run_time=individual_run_time).move_to((bit.get_x(), 0, 0))
			)
			for i,bit in zip([0, 8], bits)
		)
		self.play(bit.animate(run_time=individual_run_time).set_color("#fff") for bit in bits)
		for i,bit in zip([0, 8], bits):
			self.bits[i] = bit

		# Shift everything right.
		new_bit = Text("0", font_size=40).move_to((-5.625, 0, 0))
		self.play(
			*[bit.animate(run_time=individual_run_time).move_to((bit.get_x() + .75, 0, 0)) for bit in self.bits],
			FadeOut(self.bits[15], run_time=individual_run_time),
			FadeIn(new_bit, run_time=individual_run_time),
		)
		self.bits = [new_bit] + self.bits[0:15]

		self.play(FadeOut(text, run_time=individual_run_time))


class LfsrNormal(LfsrScene):
	def construct(self):
		super().construct()
		self.wait(1)
		self.trigger()
		self.wait(1)
		self.step(1)
		self.set_short(True)
		self.step(.5)
		for i in range(20):
			self.step()
		self.wait(1)

class LfsrLockup(LfsrScene):
	def construct(self):
		super().construct()
		self.trigger()
		for _ in range(15):
			self.step()
		self.set_short(True)
		for _ in range(9):
			self.step()
