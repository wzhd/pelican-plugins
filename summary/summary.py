"""
Summary
-------
This plugin allows easy, variable length summaries directly embedded into the
body of your articles.
"""

import types

from pelican import signals

def initialized(pelican):
    from pelican.settings import DEFAULT_CONFIG
    DEFAULT_CONFIG.setdefault('SUMMARY_BEGIN_MARKER',
                              '<!-- PELICAN_BEGIN_SUMMARY -->')
    DEFAULT_CONFIG.setdefault('SUMMARY_END_MARKER',
                              '<!-- PELICAN_END_SUMMARY -->')
    if pelican:
        pelican.settings.setdefault('SUMMARY_BEGIN_MARKER',
                                    '<!-- PELICAN_BEGIN_SUMMARY -->')
        pelican.settings.setdefault('SUMMARY_END_MARKER',
                                    '<!-- PELICAN_END_SUMMARY -->')

def content_object_init(instance):
    # if summary is already specified, use it
    if 'summary' in instance.metadata:
        return

    def _get_content(self):
        content = self._content
        if self.settings['SUMMARY_BEGIN_MARKER']:
            content = content.replace(
                self.settings['SUMMARY_BEGIN_MARKER'], '', 1)
        if self.settings['SUMMARY_END_MARKER']:
            content = content.replace(
                self.settings['SUMMARY_END_MARKER'], '', 1)
        return content
    instance._get_content = types.MethodType(_get_content, instance)

    # extract out our summary
    if not hasattr(instance, '_summary') and instance._content is not None:
        content = instance._content
        begin_summary = -1
        end_summary = -1
        last_end = 0
        summary = None
        while last_end != -1 and last_end < len(content):
            if instance.settings['SUMMARY_BEGIN_MARKER']:
                begin_summary = content.find(instance.settings['SUMMARY_BEGIN_MARKER'], last_end)
            if instance.settings['SUMMARY_END_MARKER']:
                end_summary = content.find(instance.settings['SUMMARY_END_MARKER'], last_end)
            if end_summary == -1:
                last_end = -1
            else:
                last_end = end_summary + len(instance.settings['SUMMARY_END_MARKER'])
            if summary is None:  # first time
                if begin_summary != -1 or end_summary != -1:
                    # the beginning position has to take into account the length
                    # of the marker
                    begin_summary = (begin_summary +
                                    len(instance.settings['SUMMARY_BEGIN_MARKER'])
                                    if begin_summary != -1 else 0)
                    end_summary = end_summary if end_summary != -1 else None
                    summary = instance._update_content(content[begin_summary:end_summary], instance._context.get('localsiteurl', ''))
            else:
                if begin_summary == -1 or end_summary == -1:
                    break
                begin_summary = (begin_summary +
                                len(instance.settings['SUMMARY_BEGIN_MARKER'])
                                if begin_summary != -1 else 0)
                end_summary = end_summary if end_summary != -1 else None
                summary += instance._update_content(content[begin_summary:end_summary], instance._context.get('localsiteurl', ''))
        if summary is not None:
            instance._summary = summary


def register():
    signals.initialized.connect(initialized)
    signals.content_object_init.connect(content_object_init)

