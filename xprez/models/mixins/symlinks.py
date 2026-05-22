from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SymlinkMixin:
    """Mixin for symlink models that must not form render-time cycles.

    Subclasses must implement _symlink_targets(cls, node_id).
    Override _symlink_from_id() when the from-node is not self.pk
    (e.g. ContainerSymlink uses self.container_id).
    """

    @staticmethod
    def _symlink_creates_cycle(from_id, to_id, next_ids_fn):
        if from_id == to_id:
            return True
        seen, stack = set(), [to_id]
        while stack:
            cur = stack.pop()
            if cur == from_id:
                return True
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(next_ids_fn(cur))
        return False

    @classmethod
    def _symlink_targets(cls, node_id):
        """
        Return an iterable of ids that `node_id` symlinks to (edges-out).
        Containers may have many outgoing symlinks; module symlinks have 0 or 1.
        """
        raise NotImplementedError

    @classmethod
    def would_create_cycle(cls, from_id, to_id):
        return cls._symlink_creates_cycle(from_id, to_id, cls._symlink_targets)

    def _symlink_from_id(self):
        return self.pk

    def _symlink_cycle_clean(self):
        if self.symlink_id is not None and self.would_create_cycle(
            self._symlink_from_id(), self.symlink_id
        ):
            raise ValidationError(_("Symlink would create a cycle."))

    def save(self, *args, **kwargs):
        self._symlink_cycle_clean()
        super().save(*args, **kwargs)
