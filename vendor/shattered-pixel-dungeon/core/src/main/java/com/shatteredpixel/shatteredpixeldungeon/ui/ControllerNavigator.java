package com.shatteredpixel.shatteredpixeldungeon.ui;

import com.shatteredpixel.shatteredpixeldungeon.SPDAction;
import com.watabou.input.ControllerHandler;
import com.watabou.input.GameAction;
import com.watabou.noosa.Camera;
import com.watabou.noosa.Gizmo;
import com.watabou.noosa.Group;
import com.watabou.utils.Point;
import com.watabou.utils.PointF;

import java.util.ArrayList;

/** Moves the controller's virtual cursor between usable UI buttons. */
public class ControllerNavigator {

	private Button focused;

	public void clear() {
		focused = null;
	}

	public boolean move(Group root, GameAction action) {
		int dx = 0;
		int dy = 0;
		if (action == SPDAction.N) dy = -1;
		else if (action == SPDAction.S) dy = 1;
		else if (action == SPDAction.W) dx = -1;
		else if (action == SPDAction.E) dx = 1;
		else return false;

		ArrayList<Button> buttons = new ArrayList<>();
		collectButtons(root, buttons);
		if (buttons.isEmpty()) return false;

		if (!buttons.contains(focused)) {
			focused = buttons.get(0);
		}

		Point origin = screenCenter(focused);
		Button next = null;
		float bestScore = Float.MAX_VALUE;
		for (Button candidate : buttons) {
			if (candidate == focused) continue;
			Point point = screenCenter(candidate);
			float primary = dx != 0 ? (point.x - origin.x) * dx : (point.y - origin.y) * dy;
			if (primary <= 0) continue;
			float perpendicular = dx != 0 ? Math.abs(point.y - origin.y) : Math.abs(point.x - origin.x);
			float score = primary + perpendicular * 2f;
			if (score < bestScore) {
				bestScore = score;
				next = candidate;
			}
		}

		if (next != null) focused = next;
		movePointer(focused);
		return true;
	}

	private void collectButtons(Group group, ArrayList<Button> buttons) {
		for (Gizmo child : group.members()) {
			if (child instanceof Button && child.isActive() && child.isVisible()) {
				buttons.add((Button) child);
			}
			if (child instanceof Group) {
				collectButtons((Group) child, buttons);
			}
		}
	}

	private Point screenCenter(Button button) {
		Camera camera = button.camera();
		return camera.cameraToScreen(button.centerX(), button.centerY());
	}

	private void movePointer(Button button) {
		Point point = screenCenter(button);
		ControllerHandler.setControllerPointer(true);
		ControllerHandler.updateControllerPointer(new PointF(point.x, point.y), true);
	}
}
